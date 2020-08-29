class QType(Enum):
    FOREACH = 0
    FORANY = 1
    EXIST = 2


class QuantifiedLambda(object):

    def __init__(self, expr: NormExpression):
        self.expr = expr
        self.lam = expr.lam
        self.cols = []
        self.quantifiers = []

    def __contains__(self, item):
        return item in self.lam

    @property
    def VAR_OID(self):
        return self.lam.VAR_OID

    @property
    def cloned_from(self):
        return self.lam.cloned_from

    @property
    def name(self):
        return self.lam.name

    @property
    def is_functional(self):
        return self.lam.is_functional

    @property
    def atomic(self):
        return self.lam.atomic

    @property
    def nargs(self):
        return self.lam.nargs

    def fill_time(self, df):
        if self.lam.VAR_TIME not in df.columns:
            df[self.lam.VAR_TIME] = np.datetime64(datetime.utcnow())
        return df

    def fill_oid(self, df):
        var_oid = self.lam.VAR_OID
        if df.index.name == var_oid:
            return df

        if var_oid in df.columns:
            return df.set_index(var_oid)

        c = None
        for col in self.cols:
            if c is None:
                c = df[col].astype(str)
            else:
                c = c.str.cat(df[col].astype(str))
        df[var_oid] = c.str.encode('utf-8').apply(zlib.adler32).astype('int64')
        df = df.set_index(var_oid)
        return df

    @property
    def variables(self):
        return self.lam.variables

    @property
    def data(self):
        if len(self.cols) > 0:
            return self.lam.data.groupby(self.cols)
        else:
            return self.lam.data

    def get_type(self, name):
        return self.lam.get_type(name)

    def get_grouped_variables(self):
        from norm.models import lambdas
        variables = dict((v.name, v) for v in self.lam.variables)
        return [variables.get(col, lambdas.Any) for col in self.cols]

    def add_cols(self, qtype, cols):
        pos = len(self.cols)
        self.cols.extend(cols)
        self.quantifiers.append((qtype, pos, pos + len(cols)))

    def execute(self, context):
        return self.expr.execute(context)

    def quantify(self, df):
        if len(self.cols) == 0 or len(df) == 0:
            return df
        # assert(all([col in df.columns for col in self.cols]))
        while len(self.quantifiers) > 0:
            qtype, begin, end = self.quantifiers.pop()
            if len(df) == 0:
                continue
            if qtype == QType.EXIST:
                if begin == 0:
                    df = df.iloc[:1]
                else:
                    df = df.groupby(self.cols[:begin]).min().reset_index()
                    df.index.name = self.lam.VAR_OID
                    df[self.lam.VAR_TIME] = np.datetime64(datetime.utcnow())
            elif qtype == QType.FORANY:
                total = len(self.lam.data[self.cols[begin:end]].drop_duplicates())
                if begin == 0:
                    df = df if len(df) == total else df.iloc[0:0]
                else:
                    df['_tmp_count'] = df.groupby(self.cols[:begin])[self.cols[begin]].transform('count')
                    df = df[df['_tmp_count'] == total].drop(columns=['_tmp_count'])
        return df

