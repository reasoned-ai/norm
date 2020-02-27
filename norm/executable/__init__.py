from typing import List
import pandas as pd


class EngineError(RuntimeError):
    pass


class Results(object):
    @property
    def lam(self):
        """
        :return: Lambda declaration associated with the results
        :rtype: norm.models.norm.Lambda
        """
        raise NotImplementedError

    @property
    def bindings(self):
        """
        Variable bindings
        :return: all variables involved in the computation
        :rtype: List[norm.models.norm.variable.Variable]
        """
        raise NotImplementedError

    @property
    def data(self):
        """
        All data including positives, negatives and unknowns
        :rtype: pd.DataFrame
        """
        raise NotImplementedError

    @property
    def positives(self):
        """
        Positive results
        :rtype: pd.DataFrame
        """
        raise NotImplementedError

    @property
    def negatives(self):
        """
        Negative results
        :rtype: pd.DataFrame
        """
        raise NotImplementedError

    @property
    def unknowns(self):
        """
        Unknown results
        :rtype: pd.DataFrame
        """
        raise NotImplementedError


class NormExecutable(object):

    def __init__(self, context, dependents=None, type_=None):
        """
        :param context: Compiler provides context for execution, e.g., existing bindings
        :type context: norm.compiler.NormCompiler
        :param dependents: dependent executables
        :type dependents: List[NormExecutable]
        :param type_: the Lambda for the execution results, not necessarily for every execution
        :type type_: norm.models.norm.Lambda or None
        """
        self.stack = dependents or []
        self._lam = type_ or None
        self.context = context

    @property
    def lam(self):
        """
        Get the Lambda for the results
        :rtype: norm.models.norm.Lambda or None
        """
        return self._lam

    @lam.setter
    def lam(self, o):
        """
        Set the Lambda for the results
        :type o: norm.models.norm.Lambda
        """
        self._lam = o

    def execute(self):
        """
        Execute the command with given context
        :return: the results
        :rtype: Results or None
        """
        raise NotImplementedError

    def fill_primary(self, df):
        for var in self.variables:
            if var.primary:
                if var.name in df.columns:
                    df.loc[:, var.name] = df[var.name].fillna(var.type_.default)
                else:
                    df[var.name] = var.type_.default
        return df

    def fill_oid(self, df):
        if df.index.name == self.VAR_OID:
            return df

        if self.VAR_OID in df.columns:
            return df.set_index(self.VAR_OID)

        # if OID column is given
        oid_col = self.oid_col
        if oid_col is not None and oid_col in df.columns:
            df[self.VAR_OID] = df[oid_col]
            df = df.set_index(self.VAR_OID)
            return df

        # if OID column is given but with no value in the data
        # primary columns are used to generate the oid and backfill it

        cols = [v.name for v in self.variables if v.primary and v.name in df.columns]
        c = None
        for col in cols:
            if c is None:
                c = df[col].astype(str)
            else:
                c = c.str.cat(df[col].astype(str))
        if c is not None:
            df[self.VAR_OID] = c.str.encode('utf-8').apply(zlib.adler32).astype('int64')
            df = df.set_index(self.VAR_OID)
        else:
            df.index.rename(self.VAR_OID, inplace=True)

        if oid_col is not None:
            df[oid_col] = df.index.values
        return df

    def fill_time(self, df):
        time_col = self.time_col

        if self.VAR_TIMESTAMP not in df.columns:
            if time_col is not None and time_col in df.columns:
                df[self.VAR_TIMESTAMP] = df[time_col].astype('datetime64[ns]')
            else:
                df[self.VAR_TIMESTAMP] = np.datetime64(datetime.utcnow())
        else:
            if time_col is not None and time_col in df.columns:
                df[self.VAR_TIMESTAMP].fillna(df[time_col].astype('datetime64[ns]'), inplace=True)
            else:
                df[self.VAR_TIMESTAMP].fillna(np.datetime64(datetime.utcnow()), inplace=True)
        return df

    def _fill_label(self, df):
        if self.VAR_LABEL not in df.columns:
            df[self.VAR_LABEL] = 1.0
        else:
            df[self.VAR_LABEL].fillna(1.0, inplace=True)
        return df

    def _fill_prob(self, df):
        if self.VAR_PROB not in df.columns:
            df[self.VAR_PROB] = 1.0
        else:
            df[self.VAR_PROB].fillna(1.0, inplace=True)
        return df

    def _fill_tombstone(self, df):
        if self.VAR_TOMBSTONE not in df.columns:
            df[self.VAR_TOMBSTONE] = False
        else:
            df[self.VAR_TOMBSTONE].fillna(False, inplace=True)
        return df

    def save(self):
        """
        Save the current version
        """
        if not self.atomic:
            self._save_data()
        if self.adapted:
            self._save_model()

    def empty_data(self):
        """
        Create an empty data frame
        :return: the data frame with columns
        :rtype: DataFrame
        """
        return DataFrame(columns=self._schema_names).set_index(self.VAR_OID)

    def _load_data(self):
        """
        Load data if it exists. If the current version is not an anchor, the previous versions will be combined.
        :return: the combined data
        :rtype: DataFrame
        """
        if self._data is not None:
            return self._data

        if self.anchor:
            self._data = self.empty_data()
        elif self.cloned_from is None:
            msg = "Failed to find the anchor version. The chain is broken for {}".format(self)
            logger.error(msg)
            raise RuntimeError(msg)
        else:
            self._data = self.cloned_from._load_data()

        from norm.models.revision import DeltaRevision
        for i in range(self.current_revision + 1):
            revision = self.revisions[i]
            if isinstance(revision, DeltaRevision):
                revision.redo()

        # Choose the rows still alive and the columns specified in schema
        self._data = self._data[self._all_columns[1:]][~self._data[self.VAR_TOMBSTONE]]
        return self._data

    def _save_data(self):
        """
        Save all revisions' data
        """
        if not os.path.exists(self.folder):
            self._create_folder()

        for revision in self.revisions:
            revision.save()

    def _build_model(self):
        """
        Build an adaptable model
        TODO: to implement
        """
        pass

    def _load_model(self):
        """
        Load an adapted model
        TODO: to implement
        :return:
        """
        pass

    def _save_model(self):
        """
        Save an adapted model
        TODO: to implement
        :return:
        """
        pass


class TypeDeclaration(NormExecutable):
    """
    Declare a type
    """
    pass


class LoadData(NormExecutable):
    """
    Full scan of the data, optionally with filters
    """
    pass


class Filter(NormExecutable):
    """
    Filter data with conditions
    """
    pass


class Join(NormExecutable):
    """
    Join two or more executables together. If only one provided, it joins the current scope.
    """
    pass


class ConditionJoin(Join):
    """
    Join under conditions.
    """
    pass


class WindowJoin(ConditionJoin):
    """
    Join with windowing conditions
    """
    pass


class CrossJoin(Join):
    """
    Cross join two or more executables.
    """
    pass


class Union(NormExecutable):
    """
    Combine two or more executables together.
    """
    pass


class Difference(NormExecutable):
    """
    Negate rows from the first executable which appear in the second executable
    """
    pass


class Aggregate(NormExecutable):
    """
    Quantified executions
    """
    pass


class Pivot(NormExecutable):
    """
    Value to variable expansion
    """
    def __init__(self, context, dependents=None, variable=None, type_=None):
        """
        :param variable: the name of the variable to pivot on
        :type variable: str
        """
        super().__init__(context, dependents=dependents, type_=type_)
        self.variable = variable


class Unique(NormExecutable):
    """
    Unique values
    """
    pass


class Project(NormExecutable):
    """
    Rename or assign variables
    """
    def __init__(self, context, dependents=None, variables=None, type_=None):
        """
        :type variables: List[str]
        """
        super().__init__(context, dependents=dependents, type_=type_)
        self.variables: List[str] = variables


class Construction(NormExecutable):
    """
    Construct objects and fill values
    """
    pass


class Return(NormExecutable):
    """
    Assign results to return outputs
    """
    pass


class Implication(NormExecutable):
    """
    Implication blocks
    """
    pass


class Negation(NormExecutable):
    """
    Negate results
    """
    pass


class DefineType(NormExecutable):
    """
    Define a Lambda
    """
    pass


class CodeExecution(NormExecutable):
    """
    Execute code in Python or SQL
    """
    def __init__(self, context, dependents=None, type_=None, code=''):
        super().__init__(context, dependents=dependents, type_=type_)
        self.lam.define(code)


