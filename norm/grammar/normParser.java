// Generated from /home/ax/Workspace/norm/build/lib/norm/grammar/norm.g4 by ANTLR 4.7.2
package .;
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class normParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.7.2", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		T__0=1, T__1=2, T__2=3, T__3=4, IMPL=5, CEQ=6, OEQ=7, AEQ=8, SINGLELINE=9, 
		MULTILINE=10, SPACED_EXPORT=11, EXPORT=12, SPACED_IMPORT=13, IMPORT=14, 
		SPACED_COMMAND=15, REVISIONS=16, VERSIONS=17, UNDO=18, REDO=19, DELETE=20, 
		WS=21, NS=22, LBR=23, RBR=24, LCBR=25, RCBR=26, LSBR=27, RSBR=28, NONE=29, 
		AS=30, COLON=31, SEMICOLON=32, COMMA=33, DOT=34, DOTDOT=35, IN=36, NI=37, 
		EQ=38, NE=39, GE=40, LE=41, GT=42, LT=43, LK=44, MINUS=45, PLUS=46, TIMES=47, 
		DIVIDE=48, EXP=49, MOD=50, NOT=51, AND=52, OR=53, XOR=54, IMP=55, EQV=56, 
		BOOLEAN=57, INTEGER=58, FLOAT=59, STRING=60, PATTERN=61, UUID=62, URL=63, 
		DATETIME=64, PYTHON_BLOCK=65, BLOCK_END=66, VARNAME=67;
	public static final int
		RULE_script = 0, RULE_statement = 1, RULE_comments = 2, RULE_exports = 3, 
		RULE_imports = 4, RULE_commands = 5, RULE_argumentDeclaration = 6, RULE_argumentDeclarations = 7, 
		RULE_rename = 8, RULE_renames = 9, RULE_typeDeclaration = 10, RULE_version = 11, 
		RULE_typeName = 12, RULE_variable = 13, RULE_queryProjection = 14, RULE_constant = 15, 
		RULE_code = 16, RULE_codeExpression = 17, RULE_argumentExpression = 18, 
		RULE_argumentExpressions = 19, RULE_evaluationExpression = 20, RULE_slicedExpression = 21, 
		RULE_arithmeticExpression = 22, RULE_conditionExpression = 23, RULE_oneLineExpression = 24, 
		RULE_multiLineExpression = 25, RULE_none = 26, RULE_bool_c = 27, RULE_integer_c = 28, 
		RULE_float_c = 29, RULE_string_c = 30, RULE_pattern = 31, RULE_uuid = 32, 
		RULE_url = 33, RULE_datetime = 34, RULE_logicalOperator = 35, RULE_spacedLogicalOperator = 36, 
		RULE_newlineLogicalOperator = 37, RULE_conditionOperator = 38, RULE_spacedConditionOperator = 39;
	private static String[] makeRuleNames() {
		return new String[] {
			"script", "statement", "comments", "exports", "imports", "commands", 
			"argumentDeclaration", "argumentDeclarations", "rename", "renames", "typeDeclaration", 
			"version", "typeName", "variable", "queryProjection", "constant", "code", 
			"codeExpression", "argumentExpression", "argumentExpressions", "evaluationExpression", 
			"slicedExpression", "arithmeticExpression", "conditionExpression", "oneLineExpression", 
			"multiLineExpression", "none", "bool_c", "integer_c", "float_c", "string_c", 
			"pattern", "uuid", "url", "datetime", "logicalOperator", "spacedLogicalOperator", 
			"newlineLogicalOperator", "conditionOperator", "spacedConditionOperator"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'->'", "'$latest'", "'$best'", "'?'", null, "':='", "'|='", "'&='", 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, "':'", "';'", 
			"','", "'.'", "'..'", null, null, "'=='", "'!='", "'>='", "'<='", "'>'", 
			"'<'", "'~'", "'-'", "'+'", "'*'", "'/'", "'**'", "'%'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, null, null, null, null, "IMPL", "CEQ", "OEQ", "AEQ", "SINGLELINE", 
			"MULTILINE", "SPACED_EXPORT", "EXPORT", "SPACED_IMPORT", "IMPORT", "SPACED_COMMAND", 
			"REVISIONS", "VERSIONS", "UNDO", "REDO", "DELETE", "WS", "NS", "LBR", 
			"RBR", "LCBR", "RCBR", "LSBR", "RSBR", "NONE", "AS", "COLON", "SEMICOLON", 
			"COMMA", "DOT", "DOTDOT", "IN", "NI", "EQ", "NE", "GE", "LE", "GT", "LT", 
			"LK", "MINUS", "PLUS", "TIMES", "DIVIDE", "EXP", "MOD", "NOT", "AND", 
			"OR", "XOR", "IMP", "EQV", "BOOLEAN", "INTEGER", "FLOAT", "STRING", "PATTERN", 
			"UUID", "URL", "DATETIME", "PYTHON_BLOCK", "BLOCK_END", "VARNAME"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "norm.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public normParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	public static class ScriptContext extends ParserRuleContext {
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public List<TerminalNode> SEMICOLON() { return getTokens(normParser.SEMICOLON); }
		public TerminalNode SEMICOLON(int i) {
			return getToken(normParser.SEMICOLON, i);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public ScriptContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_script; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterScript(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitScript(this);
		}
	}

	public final ScriptContext script() throws RecognitionException {
		ScriptContext _localctx = new ScriptContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_script);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(80);
			statement();
			setState(82);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS || _la==NS) {
				{
				setState(81);
				_la = _input.LA(1);
				if ( !(_la==WS || _la==NS) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
			}

			setState(84);
			match(SEMICOLON);
			setState(99);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,3,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(88);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,1,_ctx);
					while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
						if ( _alt==1 ) {
							{
							{
							setState(85);
							_la = _input.LA(1);
							if ( !(_la==WS || _la==NS) ) {
							_errHandler.recoverInline(this);
							}
							else {
								if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
								_errHandler.reportMatch(this);
								consume();
							}
							}
							} 
						}
						setState(90);
						_errHandler.sync(this);
						_alt = getInterpreter().adaptivePredict(_input,1,_ctx);
					}
					setState(91);
					statement();
					setState(93);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(92);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(95);
					match(SEMICOLON);
					}
					} 
				}
				setState(101);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,3,_ctx);
			}
			setState(103);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS || _la==NS) {
				{
				setState(102);
				_la = _input.LA(1);
				if ( !(_la==WS || _la==NS) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class StatementContext extends ParserRuleContext {
		public CommentsContext comments() {
			return getRuleContext(CommentsContext.class,0);
		}
		public ImportsContext imports() {
			return getRuleContext(ImportsContext.class,0);
		}
		public ExportsContext exports() {
			return getRuleContext(ExportsContext.class,0);
		}
		public CommandsContext commands() {
			return getRuleContext(CommandsContext.class,0);
		}
		public MultiLineExpressionContext multiLineExpression() {
			return getRuleContext(MultiLineExpressionContext.class,0);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public TypeNameContext typeName() {
			return getRuleContext(TypeNameContext.class,0);
		}
		public TerminalNode IMPL() { return getToken(normParser.IMPL, 0); }
		public TerminalNode LBR() { return getToken(normParser.LBR, 0); }
		public ArgumentDeclarationsContext argumentDeclarations() {
			return getRuleContext(ArgumentDeclarationsContext.class,0);
		}
		public TerminalNode RBR() { return getToken(normParser.RBR, 0); }
		public RenamesContext renames() {
			return getRuleContext(RenamesContext.class,0);
		}
		public CodeExpressionContext codeExpression() {
			return getRuleContext(CodeExpressionContext.class,0);
		}
		public TypeDeclarationContext typeDeclaration() {
			return getRuleContext(TypeDeclarationContext.class,0);
		}
		public StatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_statement; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterStatement(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitStatement(this);
		}
	}

	public final StatementContext statement() throws RecognitionException {
		StatementContext _localctx = new StatementContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_statement);
		int _la;
		try {
			setState(194);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,27,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(105);
				comments();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(107);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==SINGLELINE || _la==MULTILINE) {
					{
					setState(106);
					comments();
					}
				}

				setState(109);
				imports();
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(111);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==SINGLELINE || _la==MULTILINE) {
					{
					setState(110);
					comments();
					}
				}

				setState(113);
				exports();
				}
				break;
			case 4:
				enterOuterAlt(_localctx, 4);
				{
				setState(115);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==SINGLELINE || _la==MULTILINE) {
					{
					setState(114);
					comments();
					}
				}

				setState(117);
				commands();
				}
				break;
			case 5:
				enterOuterAlt(_localctx, 5);
				{
				setState(119);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==SINGLELINE || _la==MULTILINE) {
					{
					setState(118);
					comments();
					}
				}

				setState(122);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(121);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(124);
				multiLineExpression();
				}
				break;
			case 6:
				enterOuterAlt(_localctx, 6);
				{
				setState(126);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==SINGLELINE || _la==MULTILINE) {
					{
					setState(125);
					comments();
					}
				}

				setState(129);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(128);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(131);
				typeName();
				setState(133);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(132);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(135);
				match(IMPL);
				setState(137);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(136);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(139);
				match(LBR);
				setState(140);
				argumentDeclarations();
				setState(141);
				match(RBR);
				}
				break;
			case 7:
				enterOuterAlt(_localctx, 7);
				{
				setState(144);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==SINGLELINE || _la==MULTILINE) {
					{
					setState(143);
					comments();
					}
				}

				setState(147);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(146);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(149);
				typeName();
				setState(151);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(150);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(153);
				match(IMPL);
				setState(155);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(154);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(157);
				match(LBR);
				setState(158);
				renames();
				setState(159);
				match(RBR);
				}
				break;
			case 8:
				enterOuterAlt(_localctx, 8);
				{
				setState(162);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==SINGLELINE || _la==MULTILINE) {
					{
					setState(161);
					comments();
					}
				}

				setState(165);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(164);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(167);
				typeName();
				setState(169);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(168);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(171);
				match(IMPL);
				setState(173);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(172);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(175);
				codeExpression();
				}
				break;
			case 9:
				enterOuterAlt(_localctx, 9);
				{
				setState(178);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==SINGLELINE || _la==MULTILINE) {
					{
					setState(177);
					comments();
					}
				}

				setState(181);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(180);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(183);
				typeDeclaration();
				setState(192);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,26,_ctx) ) {
				case 1:
					{
					setState(185);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(184);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(187);
					match(IMPL);
					setState(189);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(188);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(191);
					multiLineExpression();
					}
					break;
				}
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class CommentsContext extends ParserRuleContext {
		public TerminalNode MULTILINE() { return getToken(normParser.MULTILINE, 0); }
		public List<TerminalNode> SINGLELINE() { return getTokens(normParser.SINGLELINE); }
		public TerminalNode SINGLELINE(int i) {
			return getToken(normParser.SINGLELINE, i);
		}
		public CommentsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_comments; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterComments(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitComments(this);
		}
	}

	public final CommentsContext comments() throws RecognitionException {
		CommentsContext _localctx = new CommentsContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_comments);
		int _la;
		try {
			setState(204);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case MULTILINE:
				enterOuterAlt(_localctx, 1);
				{
				setState(196);
				match(MULTILINE);
				}
				break;
			case SINGLELINE:
				enterOuterAlt(_localctx, 2);
				{
				setState(197);
				match(SINGLELINE);
				setState(201);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==SINGLELINE) {
					{
					{
					setState(198);
					match(SINGLELINE);
					}
					}
					setState(203);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ExportsContext extends ParserRuleContext {
		public TerminalNode SPACED_EXPORT() { return getToken(normParser.SPACED_EXPORT, 0); }
		public TypeNameContext typeName() {
			return getRuleContext(TypeNameContext.class,0);
		}
		public List<TerminalNode> VARNAME() { return getTokens(normParser.VARNAME); }
		public TerminalNode VARNAME(int i) {
			return getToken(normParser.VARNAME, i);
		}
		public List<TerminalNode> DOT() { return getTokens(normParser.DOT); }
		public TerminalNode DOT(int i) {
			return getToken(normParser.DOT, i);
		}
		public TerminalNode AS() { return getToken(normParser.AS, 0); }
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public ExportsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_exports; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterExports(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitExports(this);
		}
	}

	public final ExportsContext exports() throws RecognitionException {
		ExportsContext _localctx = new ExportsContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_exports);
		int _la;
		try {
			setState(231);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,35,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(206);
				match(SPACED_EXPORT);
				setState(207);
				typeName();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(208);
				match(SPACED_EXPORT);
				setState(209);
				typeName();
				setState(211);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(210);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(213);
				match(VARNAME);
				setState(218);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==DOT) {
					{
					{
					setState(214);
					match(DOT);
					setState(215);
					match(VARNAME);
					}
					}
					setState(220);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				setState(229);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,34,_ctx) ) {
				case 1:
					{
					setState(222);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(221);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(224);
					match(AS);
					setState(226);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(225);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(228);
					match(VARNAME);
					}
					break;
				}
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ImportsContext extends ParserRuleContext {
		public TerminalNode SPACED_IMPORT() { return getToken(normParser.SPACED_IMPORT, 0); }
		public List<TerminalNode> VARNAME() { return getTokens(normParser.VARNAME); }
		public TerminalNode VARNAME(int i) {
			return getToken(normParser.VARNAME, i);
		}
		public List<TerminalNode> DOT() { return getTokens(normParser.DOT); }
		public TerminalNode DOT(int i) {
			return getToken(normParser.DOT, i);
		}
		public TerminalNode TIMES() { return getToken(normParser.TIMES, 0); }
		public TypeNameContext typeName() {
			return getRuleContext(TypeNameContext.class,0);
		}
		public TerminalNode AS() { return getToken(normParser.AS, 0); }
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public ImportsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_imports; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterImports(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitImports(this);
		}
	}

	public final ImportsContext imports() throws RecognitionException {
		ImportsContext _localctx = new ImportsContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_imports);
		int _la;
		try {
			int _alt;
			setState(265);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,41,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(233);
				match(SPACED_IMPORT);
				setState(234);
				match(VARNAME);
				setState(239);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,36,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(235);
						match(DOT);
						setState(236);
						match(VARNAME);
						}
						} 
					}
					setState(241);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,36,_ctx);
				}
				setState(242);
				match(DOT);
				setState(243);
				match(TIMES);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(244);
				match(SPACED_IMPORT);
				setState(245);
				match(VARNAME);
				setState(250);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,37,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(246);
						match(DOT);
						setState(247);
						match(VARNAME);
						}
						} 
					}
					setState(252);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,37,_ctx);
				}
				setState(253);
				match(DOT);
				setState(254);
				typeName();
				setState(263);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,40,_ctx) ) {
				case 1:
					{
					setState(256);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(255);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(258);
					match(AS);
					setState(260);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(259);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(262);
					match(VARNAME);
					}
					break;
				}
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class CommandsContext extends ParserRuleContext {
		public TerminalNode SPACED_COMMAND() { return getToken(normParser.SPACED_COMMAND, 0); }
		public TypeNameContext typeName() {
			return getRuleContext(TypeNameContext.class,0);
		}
		public CommandsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_commands; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterCommands(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitCommands(this);
		}
	}

	public final CommandsContext commands() throws RecognitionException {
		CommandsContext _localctx = new CommandsContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_commands);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(267);
			match(SPACED_COMMAND);
			setState(268);
			typeName();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ArgumentDeclarationContext extends ParserRuleContext {
		public VariableContext variable() {
			return getRuleContext(VariableContext.class,0);
		}
		public TerminalNode COLON() { return getToken(normParser.COLON, 0); }
		public TypeNameContext typeName() {
			return getRuleContext(TypeNameContext.class,0);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public ArgumentDeclarationContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_argumentDeclaration; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterArgumentDeclaration(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitArgumentDeclaration(this);
		}
	}

	public final ArgumentDeclarationContext argumentDeclaration() throws RecognitionException {
		ArgumentDeclarationContext _localctx = new ArgumentDeclarationContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_argumentDeclaration);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(270);
			variable(0);
			setState(272);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS || _la==NS) {
				{
				setState(271);
				_la = _input.LA(1);
				if ( !(_la==WS || _la==NS) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
			}

			setState(274);
			match(COLON);
			setState(276);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS || _la==NS) {
				{
				setState(275);
				_la = _input.LA(1);
				if ( !(_la==WS || _la==NS) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
			}

			setState(278);
			typeName();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ArgumentDeclarationsContext extends ParserRuleContext {
		public List<ArgumentDeclarationContext> argumentDeclaration() {
			return getRuleContexts(ArgumentDeclarationContext.class);
		}
		public ArgumentDeclarationContext argumentDeclaration(int i) {
			return getRuleContext(ArgumentDeclarationContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(normParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(normParser.COMMA, i);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public ArgumentDeclarationsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_argumentDeclarations; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterArgumentDeclarations(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitArgumentDeclarations(this);
		}
	}

	public final ArgumentDeclarationsContext argumentDeclarations() throws RecognitionException {
		ArgumentDeclarationsContext _localctx = new ArgumentDeclarationsContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_argumentDeclarations);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(280);
			argumentDeclaration();
			setState(291);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << WS) | (1L << NS) | (1L << COMMA))) != 0)) {
				{
				{
				setState(282);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(281);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(284);
				match(COMMA);
				setState(286);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(285);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(288);
				argumentDeclaration();
				}
				}
				setState(293);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class RenameContext extends ParserRuleContext {
		public List<VariableContext> variable() {
			return getRuleContexts(VariableContext.class);
		}
		public VariableContext variable(int i) {
			return getRuleContext(VariableContext.class,i);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public RenameContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_rename; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterRename(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitRename(this);
		}
	}

	public final RenameContext rename() throws RecognitionException {
		RenameContext _localctx = new RenameContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_rename);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(294);
			variable(0);
			setState(296);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS || _la==NS) {
				{
				setState(295);
				_la = _input.LA(1);
				if ( !(_la==WS || _la==NS) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
			}

			setState(298);
			match(T__0);
			setState(300);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS || _la==NS) {
				{
				setState(299);
				_la = _input.LA(1);
				if ( !(_la==WS || _la==NS) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
			}

			setState(302);
			variable(0);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class RenamesContext extends ParserRuleContext {
		public List<RenameContext> rename() {
			return getRuleContexts(RenameContext.class);
		}
		public RenameContext rename(int i) {
			return getRuleContext(RenameContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(normParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(normParser.COMMA, i);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public RenamesContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_renames; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterRenames(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitRenames(this);
		}
	}

	public final RenamesContext renames() throws RecognitionException {
		RenamesContext _localctx = new RenamesContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_renames);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(304);
			rename();
			setState(315);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << WS) | (1L << NS) | (1L << COMMA))) != 0)) {
				{
				{
				setState(306);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(305);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(308);
				match(COMMA);
				setState(310);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(309);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(312);
				rename();
				}
				}
				setState(317);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class TypeDeclarationContext extends ParserRuleContext {
		public List<TypeNameContext> typeName() {
			return getRuleContexts(TypeNameContext.class);
		}
		public TypeNameContext typeName(int i) {
			return getRuleContext(TypeNameContext.class,i);
		}
		public TerminalNode LBR() { return getToken(normParser.LBR, 0); }
		public ArgumentDeclarationsContext argumentDeclarations() {
			return getRuleContext(ArgumentDeclarationsContext.class,0);
		}
		public TerminalNode RBR() { return getToken(normParser.RBR, 0); }
		public TerminalNode COLON() { return getToken(normParser.COLON, 0); }
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public TypeDeclarationContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_typeDeclaration; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterTypeDeclaration(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitTypeDeclaration(this);
		}
	}

	public final TypeDeclarationContext typeDeclaration() throws RecognitionException {
		TypeDeclarationContext _localctx = new TypeDeclarationContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_typeDeclaration);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(318);
			typeName();
			setState(323);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==LBR) {
				{
				setState(319);
				match(LBR);
				setState(320);
				argumentDeclarations();
				setState(321);
				match(RBR);
				}
			}

			setState(333);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,55,_ctx) ) {
			case 1:
				{
				setState(326);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(325);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(328);
				match(COLON);
				setState(330);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(329);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(332);
				typeName();
				}
				break;
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class VersionContext extends ParserRuleContext {
		public TerminalNode UUID() { return getToken(normParser.UUID, 0); }
		public VersionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_version; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterVersion(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitVersion(this);
		}
	}

	public final VersionContext version() throws RecognitionException {
		VersionContext _localctx = new VersionContext(_ctx, getState());
		enterRule(_localctx, 22, RULE_version);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(335);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__1) | (1L << T__2) | (1L << UUID))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class TypeNameContext extends ParserRuleContext {
		public TerminalNode VARNAME() { return getToken(normParser.VARNAME, 0); }
		public VersionContext version() {
			return getRuleContext(VersionContext.class,0);
		}
		public TerminalNode LSBR() { return getToken(normParser.LSBR, 0); }
		public TypeNameContext typeName() {
			return getRuleContext(TypeNameContext.class,0);
		}
		public TerminalNode RSBR() { return getToken(normParser.RSBR, 0); }
		public TypeNameContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_typeName; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterTypeName(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitTypeName(this);
		}
	}

	public final TypeNameContext typeName() throws RecognitionException {
		TypeNameContext _localctx = new TypeNameContext(_ctx, getState());
		enterRule(_localctx, 24, RULE_typeName);
		int _la;
		try {
			setState(345);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case VARNAME:
				enterOuterAlt(_localctx, 1);
				{
				setState(337);
				match(VARNAME);
				setState(339);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__1) | (1L << T__2) | (1L << UUID))) != 0)) {
					{
					setState(338);
					version();
					}
				}

				}
				break;
			case LSBR:
				enterOuterAlt(_localctx, 2);
				{
				setState(341);
				match(LSBR);
				setState(342);
				typeName();
				setState(343);
				match(RSBR);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class VariableContext extends ParserRuleContext {
		public TerminalNode VARNAME() { return getToken(normParser.VARNAME, 0); }
		public VariableContext variable() {
			return getRuleContext(VariableContext.class,0);
		}
		public TerminalNode DOT() { return getToken(normParser.DOT, 0); }
		public VariableContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_variable; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterVariable(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitVariable(this);
		}
	}

	public final VariableContext variable() throws RecognitionException {
		return variable(0);
	}

	private VariableContext variable(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		VariableContext _localctx = new VariableContext(_ctx, _parentState);
		VariableContext _prevctx = _localctx;
		int _startState = 26;
		enterRecursionRule(_localctx, 26, RULE_variable, _p);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			{
			setState(348);
			match(VARNAME);
			}
			_ctx.stop = _input.LT(-1);
			setState(355);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,58,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					{
					_localctx = new VariableContext(_parentctx, _parentState);
					pushNewRecursionContext(_localctx, _startState, RULE_variable);
					setState(350);
					if (!(precpred(_ctx, 1))) throw new FailedPredicateException(this, "precpred(_ctx, 1)");
					setState(351);
					match(DOT);
					setState(352);
					match(VARNAME);
					}
					} 
				}
				setState(357);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,58,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	public static class QueryProjectionContext extends ParserRuleContext {
		public List<VariableContext> variable() {
			return getRuleContexts(VariableContext.class);
		}
		public VariableContext variable(int i) {
			return getRuleContext(VariableContext.class,i);
		}
		public TerminalNode LCBR() { return getToken(normParser.LCBR, 0); }
		public TerminalNode RCBR() { return getToken(normParser.RCBR, 0); }
		public List<TerminalNode> COMMA() { return getTokens(normParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(normParser.COMMA, i);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public TerminalNode LBR() { return getToken(normParser.LBR, 0); }
		public TerminalNode RBR() { return getToken(normParser.RBR, 0); }
		public QueryProjectionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_queryProjection; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterQueryProjection(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitQueryProjection(this);
		}
	}

	public final QueryProjectionContext queryProjection() throws RecognitionException {
		QueryProjectionContext _localctx = new QueryProjectionContext(_ctx, getState());
		enterRule(_localctx, 28, RULE_queryProjection);
		int _la;
		try {
			setState(398);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,66,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(358);
				match(T__3);
				setState(360);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,59,_ctx) ) {
				case 1:
					{
					setState(359);
					variable(0);
					}
					break;
				}
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(362);
				match(T__3);
				setState(363);
				match(LCBR);
				setState(364);
				variable(0);
				setState(375);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==WS || _la==COMMA) {
					{
					{
					setState(366);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS) {
						{
						setState(365);
						match(WS);
						}
					}

					setState(368);
					match(COMMA);
					setState(370);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS) {
						{
						setState(369);
						match(WS);
						}
					}

					setState(372);
					variable(0);
					}
					}
					setState(377);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				setState(378);
				match(RCBR);
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(380);
				match(T__3);
				setState(381);
				match(LBR);
				setState(382);
				variable(0);
				setState(393);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==WS || _la==COMMA) {
					{
					{
					setState(384);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS) {
						{
						setState(383);
						match(WS);
						}
					}

					setState(386);
					match(COMMA);
					setState(388);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS) {
						{
						setState(387);
						match(WS);
						}
					}

					setState(390);
					variable(0);
					}
					}
					setState(395);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				setState(396);
				match(RBR);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ConstantContext extends ParserRuleContext {
		public NoneContext none() {
			return getRuleContext(NoneContext.class,0);
		}
		public Bool_cContext bool_c() {
			return getRuleContext(Bool_cContext.class,0);
		}
		public Integer_cContext integer_c() {
			return getRuleContext(Integer_cContext.class,0);
		}
		public Float_cContext float_c() {
			return getRuleContext(Float_cContext.class,0);
		}
		public String_cContext string_c() {
			return getRuleContext(String_cContext.class,0);
		}
		public PatternContext pattern() {
			return getRuleContext(PatternContext.class,0);
		}
		public UuidContext uuid() {
			return getRuleContext(UuidContext.class,0);
		}
		public UrlContext url() {
			return getRuleContext(UrlContext.class,0);
		}
		public DatetimeContext datetime() {
			return getRuleContext(DatetimeContext.class,0);
		}
		public TerminalNode LSBR() { return getToken(normParser.LSBR, 0); }
		public List<ConstantContext> constant() {
			return getRuleContexts(ConstantContext.class);
		}
		public ConstantContext constant(int i) {
			return getRuleContext(ConstantContext.class,i);
		}
		public TerminalNode RSBR() { return getToken(normParser.RSBR, 0); }
		public List<TerminalNode> COMMA() { return getTokens(normParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(normParser.COMMA, i);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public ConstantContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_constant; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterConstant(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitConstant(this);
		}
	}

	public final ConstantContext constant() throws RecognitionException {
		ConstantContext _localctx = new ConstantContext(_ctx, getState());
		enterRule(_localctx, 30, RULE_constant);
		int _la;
		try {
			setState(426);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case NONE:
				enterOuterAlt(_localctx, 1);
				{
				setState(400);
				none();
				}
				break;
			case BOOLEAN:
				enterOuterAlt(_localctx, 2);
				{
				setState(401);
				bool_c();
				}
				break;
			case INTEGER:
				enterOuterAlt(_localctx, 3);
				{
				setState(402);
				integer_c();
				}
				break;
			case FLOAT:
				enterOuterAlt(_localctx, 4);
				{
				setState(403);
				float_c();
				}
				break;
			case STRING:
				enterOuterAlt(_localctx, 5);
				{
				setState(404);
				string_c();
				}
				break;
			case PATTERN:
				enterOuterAlt(_localctx, 6);
				{
				setState(405);
				pattern();
				}
				break;
			case UUID:
				enterOuterAlt(_localctx, 7);
				{
				setState(406);
				uuid();
				}
				break;
			case URL:
				enterOuterAlt(_localctx, 8);
				{
				setState(407);
				url();
				}
				break;
			case DATETIME:
				enterOuterAlt(_localctx, 9);
				{
				setState(408);
				datetime();
				}
				break;
			case LSBR:
				enterOuterAlt(_localctx, 10);
				{
				setState(409);
				match(LSBR);
				setState(410);
				constant();
				setState(421);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==WS || _la==COMMA) {
					{
					{
					setState(412);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS) {
						{
						setState(411);
						match(WS);
						}
					}

					setState(414);
					match(COMMA);
					setState(416);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS) {
						{
						setState(415);
						match(WS);
						}
					}

					setState(418);
					constant();
					}
					}
					setState(423);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				setState(424);
				match(RSBR);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class CodeContext extends ParserRuleContext {
		public List<TerminalNode> PYTHON_BLOCK() { return getTokens(normParser.PYTHON_BLOCK); }
		public TerminalNode PYTHON_BLOCK(int i) {
			return getToken(normParser.PYTHON_BLOCK, i);
		}
		public List<TerminalNode> BLOCK_END() { return getTokens(normParser.BLOCK_END); }
		public TerminalNode BLOCK_END(int i) {
			return getToken(normParser.BLOCK_END, i);
		}
		public CodeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_code; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterCode(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitCode(this);
		}
	}

	public final CodeContext code() throws RecognitionException {
		CodeContext _localctx = new CodeContext(_ctx, getState());
		enterRule(_localctx, 32, RULE_code);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(431);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__0) | (1L << T__1) | (1L << T__2) | (1L << T__3) | (1L << IMPL) | (1L << CEQ) | (1L << OEQ) | (1L << AEQ) | (1L << SINGLELINE) | (1L << MULTILINE) | (1L << SPACED_EXPORT) | (1L << EXPORT) | (1L << SPACED_IMPORT) | (1L << IMPORT) | (1L << SPACED_COMMAND) | (1L << REVISIONS) | (1L << VERSIONS) | (1L << UNDO) | (1L << REDO) | (1L << DELETE) | (1L << WS) | (1L << NS) | (1L << LBR) | (1L << RBR) | (1L << LCBR) | (1L << RCBR) | (1L << LSBR) | (1L << RSBR) | (1L << NONE) | (1L << AS) | (1L << COLON) | (1L << SEMICOLON) | (1L << COMMA) | (1L << DOT) | (1L << DOTDOT) | (1L << IN) | (1L << NI) | (1L << EQ) | (1L << NE) | (1L << GE) | (1L << LE) | (1L << GT) | (1L << LT) | (1L << LK) | (1L << MINUS) | (1L << PLUS) | (1L << TIMES) | (1L << DIVIDE) | (1L << EXP) | (1L << MOD) | (1L << NOT) | (1L << AND) | (1L << OR) | (1L << XOR) | (1L << IMP) | (1L << EQV) | (1L << BOOLEAN) | (1L << INTEGER) | (1L << FLOAT) | (1L << STRING) | (1L << PATTERN) | (1L << UUID) | (1L << URL))) != 0) || _la==DATETIME || _la==VARNAME) {
				{
				{
				setState(428);
				_la = _input.LA(1);
				if ( _la <= 0 || (_la==PYTHON_BLOCK || _la==BLOCK_END) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
				}
				setState(433);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class CodeExpressionContext extends ParserRuleContext {
		public TerminalNode PYTHON_BLOCK() { return getToken(normParser.PYTHON_BLOCK, 0); }
		public CodeContext code() {
			return getRuleContext(CodeContext.class,0);
		}
		public TerminalNode BLOCK_END() { return getToken(normParser.BLOCK_END, 0); }
		public CodeExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_codeExpression; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterCodeExpression(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitCodeExpression(this);
		}
	}

	public final CodeExpressionContext codeExpression() throws RecognitionException {
		CodeExpressionContext _localctx = new CodeExpressionContext(_ctx, getState());
		enterRule(_localctx, 34, RULE_codeExpression);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(434);
			match(PYTHON_BLOCK);
			setState(435);
			code();
			setState(436);
			match(BLOCK_END);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ArgumentExpressionContext extends ParserRuleContext {
		public ArithmeticExpressionContext arithmeticExpression() {
			return getRuleContext(ArithmeticExpressionContext.class,0);
		}
		public QueryProjectionContext queryProjection() {
			return getRuleContext(QueryProjectionContext.class,0);
		}
		public VariableContext variable() {
			return getRuleContext(VariableContext.class,0);
		}
		public TerminalNode AS() { return getToken(normParser.AS, 0); }
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public SpacedConditionOperatorContext spacedConditionOperator() {
			return getRuleContext(SpacedConditionOperatorContext.class,0);
		}
		public ArgumentExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_argumentExpression; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterArgumentExpression(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitArgumentExpression(this);
		}
	}

	public final ArgumentExpressionContext argumentExpression() throws RecognitionException {
		ArgumentExpressionContext _localctx = new ArgumentExpressionContext(_ctx, getState());
		enterRule(_localctx, 36, RULE_argumentExpression);
		int _la;
		try {
			setState(461);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,76,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(438);
				arithmeticExpression(0);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(439);
				queryProjection();
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(440);
				variable(0);
				setState(441);
				queryProjection();
				}
				break;
			case 4:
				enterOuterAlt(_localctx, 4);
				{
				setState(443);
				variable(0);
				setState(445);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(444);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(447);
				match(AS);
				setState(449);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(448);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(451);
				arithmeticExpression(0);
				setState(453);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==T__3) {
					{
					setState(452);
					queryProjection();
					}
				}

				}
				break;
			case 5:
				enterOuterAlt(_localctx, 5);
				{
				setState(455);
				variable(0);
				setState(456);
				spacedConditionOperator();
				setState(457);
				arithmeticExpression(0);
				setState(459);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==T__3) {
					{
					setState(458);
					queryProjection();
					}
				}

				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ArgumentExpressionsContext extends ParserRuleContext {
		public TerminalNode LBR() { return getToken(normParser.LBR, 0); }
		public TerminalNode RBR() { return getToken(normParser.RBR, 0); }
		public List<ArgumentExpressionContext> argumentExpression() {
			return getRuleContexts(ArgumentExpressionContext.class);
		}
		public ArgumentExpressionContext argumentExpression(int i) {
			return getRuleContext(ArgumentExpressionContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(normParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(normParser.COMMA, i);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public ArgumentExpressionsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_argumentExpressions; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterArgumentExpressions(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitArgumentExpressions(this);
		}
	}

	public final ArgumentExpressionsContext argumentExpressions() throws RecognitionException {
		ArgumentExpressionsContext _localctx = new ArgumentExpressionsContext(_ctx, getState());
		enterRule(_localctx, 38, RULE_argumentExpressions);
		int _la;
		try {
			setState(482);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,80,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(463);
				match(LBR);
				setState(464);
				match(RBR);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(465);
				match(LBR);
				setState(466);
				argumentExpression();
				setState(477);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << WS) | (1L << NS) | (1L << COMMA))) != 0)) {
					{
					{
					setState(468);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(467);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(470);
					match(COMMA);
					setState(472);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(471);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(474);
					argumentExpression();
					}
					}
					setState(479);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				setState(480);
				match(RBR);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class EvaluationExpressionContext extends ParserRuleContext {
		public ConstantContext constant() {
			return getRuleContext(ConstantContext.class,0);
		}
		public VariableContext variable() {
			return getRuleContext(VariableContext.class,0);
		}
		public ArgumentExpressionsContext argumentExpressions() {
			return getRuleContext(ArgumentExpressionsContext.class,0);
		}
		public List<EvaluationExpressionContext> evaluationExpression() {
			return getRuleContexts(EvaluationExpressionContext.class);
		}
		public EvaluationExpressionContext evaluationExpression(int i) {
			return getRuleContext(EvaluationExpressionContext.class,i);
		}
		public TerminalNode DOT() { return getToken(normParser.DOT, 0); }
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public EvaluationExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_evaluationExpression; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterEvaluationExpression(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitEvaluationExpression(this);
		}
	}

	public final EvaluationExpressionContext evaluationExpression() throws RecognitionException {
		return evaluationExpression(0);
	}

	private EvaluationExpressionContext evaluationExpression(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		EvaluationExpressionContext _localctx = new EvaluationExpressionContext(_ctx, _parentState);
		EvaluationExpressionContext _prevctx = _localctx;
		int _startState = 40;
		enterRecursionRule(_localctx, 40, RULE_evaluationExpression, _p);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(491);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,81,_ctx) ) {
			case 1:
				{
				setState(485);
				constant();
				}
				break;
			case 2:
				{
				setState(486);
				variable(0);
				}
				break;
			case 3:
				{
				setState(487);
				argumentExpressions();
				}
				break;
			case 4:
				{
				setState(488);
				variable(0);
				setState(489);
				argumentExpressions();
				}
				break;
			}
			_ctx.stop = _input.LT(-1);
			setState(504);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,84,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					{
					_localctx = new EvaluationExpressionContext(_parentctx, _parentState);
					pushNewRecursionContext(_localctx, _startState, RULE_evaluationExpression);
					setState(493);
					if (!(precpred(_ctx, 1))) throw new FailedPredicateException(this, "precpred(_ctx, 1)");
					setState(495);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(494);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(497);
					match(DOT);
					setState(499);
					_errHandler.sync(this);
					_la = _input.LA(1);
					if (_la==WS || _la==NS) {
						{
						setState(498);
						_la = _input.LA(1);
						if ( !(_la==WS || _la==NS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						}
					}

					setState(501);
					evaluationExpression(2);
					}
					} 
				}
				setState(506);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,84,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	public static class SlicedExpressionContext extends ParserRuleContext {
		public List<EvaluationExpressionContext> evaluationExpression() {
			return getRuleContexts(EvaluationExpressionContext.class);
		}
		public EvaluationExpressionContext evaluationExpression(int i) {
			return getRuleContext(EvaluationExpressionContext.class,i);
		}
		public TerminalNode LSBR() { return getToken(normParser.LSBR, 0); }
		public TerminalNode RSBR() { return getToken(normParser.RSBR, 0); }
		public List<Integer_cContext> integer_c() {
			return getRuleContexts(Integer_cContext.class);
		}
		public Integer_cContext integer_c(int i) {
			return getRuleContext(Integer_cContext.class,i);
		}
		public TerminalNode COLON() { return getToken(normParser.COLON, 0); }
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public SlicedExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_slicedExpression; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterSlicedExpression(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitSlicedExpression(this);
		}
	}

	public final SlicedExpressionContext slicedExpression() throws RecognitionException {
		SlicedExpressionContext _localctx = new SlicedExpressionContext(_ctx, getState());
		enterRule(_localctx, 42, RULE_slicedExpression);
		int _la;
		try {
			setState(532);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,90,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(507);
				evaluationExpression(0);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(508);
				evaluationExpression(0);
				setState(509);
				match(LSBR);
				setState(511);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,85,_ctx) ) {
				case 1:
					{
					setState(510);
					integer_c();
					}
					break;
				}
				setState(514);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,86,_ctx) ) {
				case 1:
					{
					setState(513);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
					break;
				}
				setState(517);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==COLON) {
					{
					setState(516);
					match(COLON);
					}
				}

				setState(520);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS || _la==NS) {
					{
					setState(519);
					_la = _input.LA(1);
					if ( !(_la==WS || _la==NS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					}
				}

				setState(523);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==INTEGER) {
					{
					setState(522);
					integer_c();
					}
				}

				setState(525);
				match(RSBR);
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(527);
				evaluationExpression(0);
				setState(528);
				match(LSBR);
				setState(529);
				evaluationExpression(0);
				setState(530);
				match(RSBR);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ArithmeticExpressionContext extends ParserRuleContext {
		public SlicedExpressionContext slicedExpression() {
			return getRuleContext(SlicedExpressionContext.class,0);
		}
		public TerminalNode LBR() { return getToken(normParser.LBR, 0); }
		public List<ArithmeticExpressionContext> arithmeticExpression() {
			return getRuleContexts(ArithmeticExpressionContext.class);
		}
		public ArithmeticExpressionContext arithmeticExpression(int i) {
			return getRuleContext(ArithmeticExpressionContext.class,i);
		}
		public TerminalNode RBR() { return getToken(normParser.RBR, 0); }
		public TerminalNode MINUS() { return getToken(normParser.MINUS, 0); }
		public TerminalNode MOD() { return getToken(normParser.MOD, 0); }
		public TerminalNode EXP() { return getToken(normParser.EXP, 0); }
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public TerminalNode TIMES() { return getToken(normParser.TIMES, 0); }
		public TerminalNode DIVIDE() { return getToken(normParser.DIVIDE, 0); }
		public TerminalNode PLUS() { return getToken(normParser.PLUS, 0); }
		public ArithmeticExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_arithmeticExpression; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterArithmeticExpression(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitArithmeticExpression(this);
		}
	}

	public final ArithmeticExpressionContext arithmeticExpression() throws RecognitionException {
		return arithmeticExpression(0);
	}

	private ArithmeticExpressionContext arithmeticExpression(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		ArithmeticExpressionContext _localctx = new ArithmeticExpressionContext(_ctx, _parentState);
		ArithmeticExpressionContext _prevctx = _localctx;
		int _startState = 44;
		enterRecursionRule(_localctx, 44, RULE_arithmeticExpression, _p);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(542);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,91,_ctx) ) {
			case 1:
				{
				setState(535);
				slicedExpression();
				}
				break;
			case 2:
				{
				setState(536);
				match(LBR);
				setState(537);
				arithmeticExpression(0);
				setState(538);
				match(RBR);
				}
				break;
			case 3:
				{
				setState(540);
				match(MINUS);
				setState(541);
				arithmeticExpression(4);
				}
				break;
			}
			_ctx.stop = _input.LT(-1);
			setState(573);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,99,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					setState(571);
					_errHandler.sync(this);
					switch ( getInterpreter().adaptivePredict(_input,98,_ctx) ) {
					case 1:
						{
						_localctx = new ArithmeticExpressionContext(_parentctx, _parentState);
						pushNewRecursionContext(_localctx, _startState, RULE_arithmeticExpression);
						setState(544);
						if (!(precpred(_ctx, 3))) throw new FailedPredicateException(this, "precpred(_ctx, 3)");
						setState(546);
						_errHandler.sync(this);
						_la = _input.LA(1);
						if (_la==WS || _la==NS) {
							{
							setState(545);
							_la = _input.LA(1);
							if ( !(_la==WS || _la==NS) ) {
							_errHandler.recoverInline(this);
							}
							else {
								if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
								_errHandler.reportMatch(this);
								consume();
							}
							}
						}

						setState(548);
						_la = _input.LA(1);
						if ( !(_la==EXP || _la==MOD) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						setState(550);
						_errHandler.sync(this);
						_la = _input.LA(1);
						if (_la==WS || _la==NS) {
							{
							setState(549);
							_la = _input.LA(1);
							if ( !(_la==WS || _la==NS) ) {
							_errHandler.recoverInline(this);
							}
							else {
								if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
								_errHandler.reportMatch(this);
								consume();
							}
							}
						}

						setState(552);
						arithmeticExpression(4);
						}
						break;
					case 2:
						{
						_localctx = new ArithmeticExpressionContext(_parentctx, _parentState);
						pushNewRecursionContext(_localctx, _startState, RULE_arithmeticExpression);
						setState(553);
						if (!(precpred(_ctx, 2))) throw new FailedPredicateException(this, "precpred(_ctx, 2)");
						setState(555);
						_errHandler.sync(this);
						_la = _input.LA(1);
						if (_la==WS || _la==NS) {
							{
							setState(554);
							_la = _input.LA(1);
							if ( !(_la==WS || _la==NS) ) {
							_errHandler.recoverInline(this);
							}
							else {
								if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
								_errHandler.reportMatch(this);
								consume();
							}
							}
						}

						setState(557);
						_la = _input.LA(1);
						if ( !(_la==TIMES || _la==DIVIDE) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						setState(559);
						_errHandler.sync(this);
						_la = _input.LA(1);
						if (_la==WS || _la==NS) {
							{
							setState(558);
							_la = _input.LA(1);
							if ( !(_la==WS || _la==NS) ) {
							_errHandler.recoverInline(this);
							}
							else {
								if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
								_errHandler.reportMatch(this);
								consume();
							}
							}
						}

						setState(561);
						arithmeticExpression(3);
						}
						break;
					case 3:
						{
						_localctx = new ArithmeticExpressionContext(_parentctx, _parentState);
						pushNewRecursionContext(_localctx, _startState, RULE_arithmeticExpression);
						setState(562);
						if (!(precpred(_ctx, 1))) throw new FailedPredicateException(this, "precpred(_ctx, 1)");
						setState(564);
						_errHandler.sync(this);
						_la = _input.LA(1);
						if (_la==WS || _la==NS) {
							{
							setState(563);
							_la = _input.LA(1);
							if ( !(_la==WS || _la==NS) ) {
							_errHandler.recoverInline(this);
							}
							else {
								if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
								_errHandler.reportMatch(this);
								consume();
							}
							}
						}

						setState(566);
						_la = _input.LA(1);
						if ( !(_la==MINUS || _la==PLUS) ) {
						_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						setState(568);
						_errHandler.sync(this);
						_la = _input.LA(1);
						if (_la==WS || _la==NS) {
							{
							setState(567);
							_la = _input.LA(1);
							if ( !(_la==WS || _la==NS) ) {
							_errHandler.recoverInline(this);
							}
							else {
								if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
								_errHandler.reportMatch(this);
								consume();
							}
							}
						}

						setState(570);
						arithmeticExpression(2);
						}
						break;
					}
					} 
				}
				setState(575);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,99,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	public static class ConditionExpressionContext extends ParserRuleContext {
		public List<ArithmeticExpressionContext> arithmeticExpression() {
			return getRuleContexts(ArithmeticExpressionContext.class);
		}
		public ArithmeticExpressionContext arithmeticExpression(int i) {
			return getRuleContext(ArithmeticExpressionContext.class,i);
		}
		public SpacedConditionOperatorContext spacedConditionOperator() {
			return getRuleContext(SpacedConditionOperatorContext.class,0);
		}
		public ConditionExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_conditionExpression; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterConditionExpression(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitConditionExpression(this);
		}
	}

	public final ConditionExpressionContext conditionExpression() throws RecognitionException {
		ConditionExpressionContext _localctx = new ConditionExpressionContext(_ctx, getState());
		enterRule(_localctx, 46, RULE_conditionExpression);
		try {
			setState(581);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,100,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(576);
				arithmeticExpression(0);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(577);
				arithmeticExpression(0);
				setState(578);
				spacedConditionOperator();
				setState(579);
				arithmeticExpression(0);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class OneLineExpressionContext extends ParserRuleContext {
		public ConditionExpressionContext conditionExpression() {
			return getRuleContext(ConditionExpressionContext.class,0);
		}
		public TerminalNode WS() { return getToken(normParser.WS, 0); }
		public QueryProjectionContext queryProjection() {
			return getRuleContext(QueryProjectionContext.class,0);
		}
		public TerminalNode NOT() { return getToken(normParser.NOT, 0); }
		public List<OneLineExpressionContext> oneLineExpression() {
			return getRuleContexts(OneLineExpressionContext.class);
		}
		public OneLineExpressionContext oneLineExpression(int i) {
			return getRuleContext(OneLineExpressionContext.class,i);
		}
		public SpacedLogicalOperatorContext spacedLogicalOperator() {
			return getRuleContext(SpacedLogicalOperatorContext.class,0);
		}
		public OneLineExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_oneLineExpression; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterOneLineExpression(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitOneLineExpression(this);
		}
	}

	public final OneLineExpressionContext oneLineExpression() throws RecognitionException {
		return oneLineExpression(0);
	}

	private OneLineExpressionContext oneLineExpression(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		OneLineExpressionContext _localctx = new OneLineExpressionContext(_ctx, _parentState);
		OneLineExpressionContext _prevctx = _localctx;
		int _startState = 48;
		enterRecursionRule(_localctx, 48, RULE_oneLineExpression, _p);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(596);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case LBR:
			case LSBR:
			case NONE:
			case MINUS:
			case BOOLEAN:
			case INTEGER:
			case FLOAT:
			case STRING:
			case PATTERN:
			case UUID:
			case URL:
			case DATETIME:
			case VARNAME:
				{
				setState(584);
				conditionExpression();
				setState(586);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,101,_ctx) ) {
				case 1:
					{
					setState(585);
					match(WS);
					}
					break;
				}
				setState(589);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,102,_ctx) ) {
				case 1:
					{
					setState(588);
					queryProjection();
					}
					break;
				}
				}
				break;
			case NOT:
				{
				setState(591);
				match(NOT);
				setState(593);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==WS) {
					{
					setState(592);
					match(WS);
					}
				}

				setState(595);
				oneLineExpression(2);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
			_ctx.stop = _input.LT(-1);
			setState(604);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,105,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					{
					_localctx = new OneLineExpressionContext(_parentctx, _parentState);
					pushNewRecursionContext(_localctx, _startState, RULE_oneLineExpression);
					setState(598);
					if (!(precpred(_ctx, 1))) throw new FailedPredicateException(this, "precpred(_ctx, 1)");
					setState(599);
					spacedLogicalOperator();
					setState(600);
					oneLineExpression(2);
					}
					} 
				}
				setState(606);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,105,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	public static class MultiLineExpressionContext extends ParserRuleContext {
		public OneLineExpressionContext oneLineExpression() {
			return getRuleContext(OneLineExpressionContext.class,0);
		}
		public NewlineLogicalOperatorContext newlineLogicalOperator() {
			return getRuleContext(NewlineLogicalOperatorContext.class,0);
		}
		public MultiLineExpressionContext multiLineExpression() {
			return getRuleContext(MultiLineExpressionContext.class,0);
		}
		public MultiLineExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_multiLineExpression; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterMultiLineExpression(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitMultiLineExpression(this);
		}
	}

	public final MultiLineExpressionContext multiLineExpression() throws RecognitionException {
		MultiLineExpressionContext _localctx = new MultiLineExpressionContext(_ctx, getState());
		enterRule(_localctx, 50, RULE_multiLineExpression);
		try {
			setState(612);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,106,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(607);
				oneLineExpression(0);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(608);
				oneLineExpression(0);
				setState(609);
				newlineLogicalOperator();
				setState(610);
				multiLineExpression();
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class NoneContext extends ParserRuleContext {
		public TerminalNode NONE() { return getToken(normParser.NONE, 0); }
		public NoneContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_none; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterNone(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitNone(this);
		}
	}

	public final NoneContext none() throws RecognitionException {
		NoneContext _localctx = new NoneContext(_ctx, getState());
		enterRule(_localctx, 52, RULE_none);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(614);
			match(NONE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Bool_cContext extends ParserRuleContext {
		public TerminalNode BOOLEAN() { return getToken(normParser.BOOLEAN, 0); }
		public Bool_cContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_bool_c; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterBool_c(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitBool_c(this);
		}
	}

	public final Bool_cContext bool_c() throws RecognitionException {
		Bool_cContext _localctx = new Bool_cContext(_ctx, getState());
		enterRule(_localctx, 54, RULE_bool_c);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(616);
			match(BOOLEAN);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Integer_cContext extends ParserRuleContext {
		public TerminalNode INTEGER() { return getToken(normParser.INTEGER, 0); }
		public Integer_cContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_integer_c; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterInteger_c(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitInteger_c(this);
		}
	}

	public final Integer_cContext integer_c() throws RecognitionException {
		Integer_cContext _localctx = new Integer_cContext(_ctx, getState());
		enterRule(_localctx, 56, RULE_integer_c);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(618);
			match(INTEGER);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class Float_cContext extends ParserRuleContext {
		public TerminalNode FLOAT() { return getToken(normParser.FLOAT, 0); }
		public Float_cContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_float_c; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterFloat_c(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitFloat_c(this);
		}
	}

	public final Float_cContext float_c() throws RecognitionException {
		Float_cContext _localctx = new Float_cContext(_ctx, getState());
		enterRule(_localctx, 58, RULE_float_c);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(620);
			match(FLOAT);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class String_cContext extends ParserRuleContext {
		public TerminalNode STRING() { return getToken(normParser.STRING, 0); }
		public String_cContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_string_c; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterString_c(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitString_c(this);
		}
	}

	public final String_cContext string_c() throws RecognitionException {
		String_cContext _localctx = new String_cContext(_ctx, getState());
		enterRule(_localctx, 60, RULE_string_c);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(622);
			match(STRING);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class PatternContext extends ParserRuleContext {
		public TerminalNode PATTERN() { return getToken(normParser.PATTERN, 0); }
		public PatternContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_pattern; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterPattern(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitPattern(this);
		}
	}

	public final PatternContext pattern() throws RecognitionException {
		PatternContext _localctx = new PatternContext(_ctx, getState());
		enterRule(_localctx, 62, RULE_pattern);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(624);
			match(PATTERN);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class UuidContext extends ParserRuleContext {
		public TerminalNode UUID() { return getToken(normParser.UUID, 0); }
		public UuidContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_uuid; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterUuid(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitUuid(this);
		}
	}

	public final UuidContext uuid() throws RecognitionException {
		UuidContext _localctx = new UuidContext(_ctx, getState());
		enterRule(_localctx, 64, RULE_uuid);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(626);
			match(UUID);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class UrlContext extends ParserRuleContext {
		public TerminalNode URL() { return getToken(normParser.URL, 0); }
		public UrlContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_url; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterUrl(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitUrl(this);
		}
	}

	public final UrlContext url() throws RecognitionException {
		UrlContext _localctx = new UrlContext(_ctx, getState());
		enterRule(_localctx, 66, RULE_url);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(628);
			match(URL);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class DatetimeContext extends ParserRuleContext {
		public TerminalNode DATETIME() { return getToken(normParser.DATETIME, 0); }
		public DatetimeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_datetime; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterDatetime(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitDatetime(this);
		}
	}

	public final DatetimeContext datetime() throws RecognitionException {
		DatetimeContext _localctx = new DatetimeContext(_ctx, getState());
		enterRule(_localctx, 68, RULE_datetime);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(630);
			match(DATETIME);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class LogicalOperatorContext extends ParserRuleContext {
		public TerminalNode AND() { return getToken(normParser.AND, 0); }
		public TerminalNode OR() { return getToken(normParser.OR, 0); }
		public TerminalNode NOT() { return getToken(normParser.NOT, 0); }
		public TerminalNode XOR() { return getToken(normParser.XOR, 0); }
		public TerminalNode IMP() { return getToken(normParser.IMP, 0); }
		public TerminalNode EQV() { return getToken(normParser.EQV, 0); }
		public LogicalOperatorContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_logicalOperator; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterLogicalOperator(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitLogicalOperator(this);
		}
	}

	public final LogicalOperatorContext logicalOperator() throws RecognitionException {
		LogicalOperatorContext _localctx = new LogicalOperatorContext(_ctx, getState());
		enterRule(_localctx, 70, RULE_logicalOperator);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(632);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << NOT) | (1L << AND) | (1L << OR) | (1L << XOR) | (1L << IMP) | (1L << EQV))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class SpacedLogicalOperatorContext extends ParserRuleContext {
		public LogicalOperatorContext logicalOperator() {
			return getRuleContext(LogicalOperatorContext.class,0);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public SpacedLogicalOperatorContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_spacedLogicalOperator; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterSpacedLogicalOperator(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitSpacedLogicalOperator(this);
		}
	}

	public final SpacedLogicalOperatorContext spacedLogicalOperator() throws RecognitionException {
		SpacedLogicalOperatorContext _localctx = new SpacedLogicalOperatorContext(_ctx, getState());
		enterRule(_localctx, 72, RULE_spacedLogicalOperator);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(635);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS) {
				{
				setState(634);
				match(WS);
				}
			}

			setState(637);
			logicalOperator();
			setState(639);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS) {
				{
				setState(638);
				match(WS);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class NewlineLogicalOperatorContext extends ParserRuleContext {
		public TerminalNode NS() { return getToken(normParser.NS, 0); }
		public LogicalOperatorContext logicalOperator() {
			return getRuleContext(LogicalOperatorContext.class,0);
		}
		public TerminalNode WS() { return getToken(normParser.WS, 0); }
		public NewlineLogicalOperatorContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_newlineLogicalOperator; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterNewlineLogicalOperator(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitNewlineLogicalOperator(this);
		}
	}

	public final NewlineLogicalOperatorContext newlineLogicalOperator() throws RecognitionException {
		NewlineLogicalOperatorContext _localctx = new NewlineLogicalOperatorContext(_ctx, getState());
		enterRule(_localctx, 74, RULE_newlineLogicalOperator);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(641);
			match(NS);
			setState(642);
			logicalOperator();
			setState(644);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS) {
				{
				setState(643);
				match(WS);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ConditionOperatorContext extends ParserRuleContext {
		public TerminalNode EQ() { return getToken(normParser.EQ, 0); }
		public TerminalNode NE() { return getToken(normParser.NE, 0); }
		public TerminalNode IN() { return getToken(normParser.IN, 0); }
		public TerminalNode NI() { return getToken(normParser.NI, 0); }
		public TerminalNode LT() { return getToken(normParser.LT, 0); }
		public TerminalNode LE() { return getToken(normParser.LE, 0); }
		public TerminalNode GT() { return getToken(normParser.GT, 0); }
		public TerminalNode GE() { return getToken(normParser.GE, 0); }
		public TerminalNode LK() { return getToken(normParser.LK, 0); }
		public ConditionOperatorContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_conditionOperator; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterConditionOperator(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitConditionOperator(this);
		}
	}

	public final ConditionOperatorContext conditionOperator() throws RecognitionException {
		ConditionOperatorContext _localctx = new ConditionOperatorContext(_ctx, getState());
		enterRule(_localctx, 76, RULE_conditionOperator);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(646);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << IN) | (1L << NI) | (1L << EQ) | (1L << NE) | (1L << GE) | (1L << LE) | (1L << GT) | (1L << LT) | (1L << LK))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class SpacedConditionOperatorContext extends ParserRuleContext {
		public ConditionOperatorContext conditionOperator() {
			return getRuleContext(ConditionOperatorContext.class,0);
		}
		public List<TerminalNode> WS() { return getTokens(normParser.WS); }
		public TerminalNode WS(int i) {
			return getToken(normParser.WS, i);
		}
		public List<TerminalNode> NS() { return getTokens(normParser.NS); }
		public TerminalNode NS(int i) {
			return getToken(normParser.NS, i);
		}
		public SpacedConditionOperatorContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_spacedConditionOperator; }
		@Override
		public void enterRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).enterSpacedConditionOperator(this);
		}
		@Override
		public void exitRule(ParseTreeListener listener) {
			if ( listener instanceof normListener ) ((normListener)listener).exitSpacedConditionOperator(this);
		}
	}

	public final SpacedConditionOperatorContext spacedConditionOperator() throws RecognitionException {
		SpacedConditionOperatorContext _localctx = new SpacedConditionOperatorContext(_ctx, getState());
		enterRule(_localctx, 78, RULE_spacedConditionOperator);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(649);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS || _la==NS) {
				{
				setState(648);
				_la = _input.LA(1);
				if ( !(_la==WS || _la==NS) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
			}

			setState(651);
			conditionOperator();
			setState(653);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==WS || _la==NS) {
				{
				setState(652);
				_la = _input.LA(1);
				if ( !(_la==WS || _la==NS) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public boolean sempred(RuleContext _localctx, int ruleIndex, int predIndex) {
		switch (ruleIndex) {
		case 13:
			return variable_sempred((VariableContext)_localctx, predIndex);
		case 20:
			return evaluationExpression_sempred((EvaluationExpressionContext)_localctx, predIndex);
		case 22:
			return arithmeticExpression_sempred((ArithmeticExpressionContext)_localctx, predIndex);
		case 24:
			return oneLineExpression_sempred((OneLineExpressionContext)_localctx, predIndex);
		}
		return true;
	}
	private boolean variable_sempred(VariableContext _localctx, int predIndex) {
		switch (predIndex) {
		case 0:
			return precpred(_ctx, 1);
		}
		return true;
	}
	private boolean evaluationExpression_sempred(EvaluationExpressionContext _localctx, int predIndex) {
		switch (predIndex) {
		case 1:
			return precpred(_ctx, 1);
		}
		return true;
	}
	private boolean arithmeticExpression_sempred(ArithmeticExpressionContext _localctx, int predIndex) {
		switch (predIndex) {
		case 2:
			return precpred(_ctx, 3);
		case 3:
			return precpred(_ctx, 2);
		case 4:
			return precpred(_ctx, 1);
		}
		return true;
	}
	private boolean oneLineExpression_sempred(OneLineExpressionContext _localctx, int predIndex) {
		switch (predIndex) {
		case 5:
			return precpred(_ctx, 1);
		}
		return true;
	}

	public static final String _serializedATN =
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3E\u0292\4\2\t\2\4"+
		"\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t"+
		"\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22"+
		"\4\23\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31\t\31"+
		"\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36\t\36\4\37\t\37\4 \t \4!"+
		"\t!\4\"\t\"\4#\t#\4$\t$\4%\t%\4&\t&\4\'\t\'\4(\t(\4)\t)\3\2\3\2\5\2U\n"+
		"\2\3\2\3\2\7\2Y\n\2\f\2\16\2\\\13\2\3\2\3\2\5\2`\n\2\3\2\3\2\7\2d\n\2"+
		"\f\2\16\2g\13\2\3\2\5\2j\n\2\3\3\3\3\5\3n\n\3\3\3\3\3\5\3r\n\3\3\3\3\3"+
		"\5\3v\n\3\3\3\3\3\5\3z\n\3\3\3\5\3}\n\3\3\3\3\3\5\3\u0081\n\3\3\3\5\3"+
		"\u0084\n\3\3\3\3\3\5\3\u0088\n\3\3\3\3\3\5\3\u008c\n\3\3\3\3\3\3\3\3\3"+
		"\3\3\5\3\u0093\n\3\3\3\5\3\u0096\n\3\3\3\3\3\5\3\u009a\n\3\3\3\3\3\5\3"+
		"\u009e\n\3\3\3\3\3\3\3\3\3\3\3\5\3\u00a5\n\3\3\3\5\3\u00a8\n\3\3\3\3\3"+
		"\5\3\u00ac\n\3\3\3\3\3\5\3\u00b0\n\3\3\3\3\3\3\3\5\3\u00b5\n\3\3\3\5\3"+
		"\u00b8\n\3\3\3\3\3\5\3\u00bc\n\3\3\3\3\3\5\3\u00c0\n\3\3\3\5\3\u00c3\n"+
		"\3\5\3\u00c5\n\3\3\4\3\4\3\4\7\4\u00ca\n\4\f\4\16\4\u00cd\13\4\5\4\u00cf"+
		"\n\4\3\5\3\5\3\5\3\5\3\5\5\5\u00d6\n\5\3\5\3\5\3\5\7\5\u00db\n\5\f\5\16"+
		"\5\u00de\13\5\3\5\5\5\u00e1\n\5\3\5\3\5\5\5\u00e5\n\5\3\5\5\5\u00e8\n"+
		"\5\5\5\u00ea\n\5\3\6\3\6\3\6\3\6\7\6\u00f0\n\6\f\6\16\6\u00f3\13\6\3\6"+
		"\3\6\3\6\3\6\3\6\3\6\7\6\u00fb\n\6\f\6\16\6\u00fe\13\6\3\6\3\6\3\6\5\6"+
		"\u0103\n\6\3\6\3\6\5\6\u0107\n\6\3\6\5\6\u010a\n\6\5\6\u010c\n\6\3\7\3"+
		"\7\3\7\3\b\3\b\5\b\u0113\n\b\3\b\3\b\5\b\u0117\n\b\3\b\3\b\3\t\3\t\5\t"+
		"\u011d\n\t\3\t\3\t\5\t\u0121\n\t\3\t\7\t\u0124\n\t\f\t\16\t\u0127\13\t"+
		"\3\n\3\n\5\n\u012b\n\n\3\n\3\n\5\n\u012f\n\n\3\n\3\n\3\13\3\13\5\13\u0135"+
		"\n\13\3\13\3\13\5\13\u0139\n\13\3\13\7\13\u013c\n\13\f\13\16\13\u013f"+
		"\13\13\3\f\3\f\3\f\3\f\3\f\5\f\u0146\n\f\3\f\5\f\u0149\n\f\3\f\3\f\5\f"+
		"\u014d\n\f\3\f\5\f\u0150\n\f\3\r\3\r\3\16\3\16\5\16\u0156\n\16\3\16\3"+
		"\16\3\16\3\16\5\16\u015c\n\16\3\17\3\17\3\17\3\17\3\17\3\17\7\17\u0164"+
		"\n\17\f\17\16\17\u0167\13\17\3\20\3\20\5\20\u016b\n\20\3\20\3\20\3\20"+
		"\3\20\5\20\u0171\n\20\3\20\3\20\5\20\u0175\n\20\3\20\7\20\u0178\n\20\f"+
		"\20\16\20\u017b\13\20\3\20\3\20\3\20\3\20\3\20\3\20\5\20\u0183\n\20\3"+
		"\20\3\20\5\20\u0187\n\20\3\20\7\20\u018a\n\20\f\20\16\20\u018d\13\20\3"+
		"\20\3\20\5\20\u0191\n\20\3\21\3\21\3\21\3\21\3\21\3\21\3\21\3\21\3\21"+
		"\3\21\3\21\3\21\5\21\u019f\n\21\3\21\3\21\5\21\u01a3\n\21\3\21\7\21\u01a6"+
		"\n\21\f\21\16\21\u01a9\13\21\3\21\3\21\5\21\u01ad\n\21\3\22\7\22\u01b0"+
		"\n\22\f\22\16\22\u01b3\13\22\3\23\3\23\3\23\3\23\3\24\3\24\3\24\3\24\3"+
		"\24\3\24\3\24\5\24\u01c0\n\24\3\24\3\24\5\24\u01c4\n\24\3\24\3\24\5\24"+
		"\u01c8\n\24\3\24\3\24\3\24\3\24\5\24\u01ce\n\24\5\24\u01d0\n\24\3\25\3"+
		"\25\3\25\3\25\3\25\5\25\u01d7\n\25\3\25\3\25\5\25\u01db\n\25\3\25\7\25"+
		"\u01de\n\25\f\25\16\25\u01e1\13\25\3\25\3\25\5\25\u01e5\n\25\3\26\3\26"+
		"\3\26\3\26\3\26\3\26\3\26\5\26\u01ee\n\26\3\26\3\26\5\26\u01f2\n\26\3"+
		"\26\3\26\5\26\u01f6\n\26\3\26\7\26\u01f9\n\26\f\26\16\26\u01fc\13\26\3"+
		"\27\3\27\3\27\3\27\5\27\u0202\n\27\3\27\5\27\u0205\n\27\3\27\5\27\u0208"+
		"\n\27\3\27\5\27\u020b\n\27\3\27\5\27\u020e\n\27\3\27\3\27\3\27\3\27\3"+
		"\27\3\27\3\27\5\27\u0217\n\27\3\30\3\30\3\30\3\30\3\30\3\30\3\30\3\30"+
		"\5\30\u0221\n\30\3\30\3\30\5\30\u0225\n\30\3\30\3\30\5\30\u0229\n\30\3"+
		"\30\3\30\3\30\5\30\u022e\n\30\3\30\3\30\5\30\u0232\n\30\3\30\3\30\3\30"+
		"\5\30\u0237\n\30\3\30\3\30\5\30\u023b\n\30\3\30\7\30\u023e\n\30\f\30\16"+
		"\30\u0241\13\30\3\31\3\31\3\31\3\31\3\31\5\31\u0248\n\31\3\32\3\32\3\32"+
		"\5\32\u024d\n\32\3\32\5\32\u0250\n\32\3\32\3\32\5\32\u0254\n\32\3\32\5"+
		"\32\u0257\n\32\3\32\3\32\3\32\3\32\7\32\u025d\n\32\f\32\16\32\u0260\13"+
		"\32\3\33\3\33\3\33\3\33\3\33\5\33\u0267\n\33\3\34\3\34\3\35\3\35\3\36"+
		"\3\36\3\37\3\37\3 \3 \3!\3!\3\"\3\"\3#\3#\3$\3$\3%\3%\3&\5&\u027e\n&\3"+
		"&\3&\5&\u0282\n&\3\'\3\'\3\'\5\'\u0287\n\'\3(\3(\3)\5)\u028c\n)\3)\3)"+
		"\5)\u0290\n)\3)\2\6\34*.\62*\2\4\6\b\n\f\16\20\22\24\26\30\32\34\36 \""+
		"$&(*,.\60\62\64\668:<>@BDFHJLNP\2\n\3\2\27\30\4\2\4\5@@\3\2CD\3\2\63\64"+
		"\3\2\61\62\3\2/\60\3\2\65:\3\2&.\2\u02f1\2R\3\2\2\2\4\u00c4\3\2\2\2\6"+
		"\u00ce\3\2\2\2\b\u00e9\3\2\2\2\n\u010b\3\2\2\2\f\u010d\3\2\2\2\16\u0110"+
		"\3\2\2\2\20\u011a\3\2\2\2\22\u0128\3\2\2\2\24\u0132\3\2\2\2\26\u0140\3"+
		"\2\2\2\30\u0151\3\2\2\2\32\u015b\3\2\2\2\34\u015d\3\2\2\2\36\u0190\3\2"+
		"\2\2 \u01ac\3\2\2\2\"\u01b1\3\2\2\2$\u01b4\3\2\2\2&\u01cf\3\2\2\2(\u01e4"+
		"\3\2\2\2*\u01ed\3\2\2\2,\u0216\3\2\2\2.\u0220\3\2\2\2\60\u0247\3\2\2\2"+
		"\62\u0256\3\2\2\2\64\u0266\3\2\2\2\66\u0268\3\2\2\28\u026a\3\2\2\2:\u026c"+
		"\3\2\2\2<\u026e\3\2\2\2>\u0270\3\2\2\2@\u0272\3\2\2\2B\u0274\3\2\2\2D"+
		"\u0276\3\2\2\2F\u0278\3\2\2\2H\u027a\3\2\2\2J\u027d\3\2\2\2L\u0283\3\2"+
		"\2\2N\u0288\3\2\2\2P\u028b\3\2\2\2RT\5\4\3\2SU\t\2\2\2TS\3\2\2\2TU\3\2"+
		"\2\2UV\3\2\2\2Ve\7\"\2\2WY\t\2\2\2XW\3\2\2\2Y\\\3\2\2\2ZX\3\2\2\2Z[\3"+
		"\2\2\2[]\3\2\2\2\\Z\3\2\2\2]_\5\4\3\2^`\t\2\2\2_^\3\2\2\2_`\3\2\2\2`a"+
		"\3\2\2\2ab\7\"\2\2bd\3\2\2\2cZ\3\2\2\2dg\3\2\2\2ec\3\2\2\2ef\3\2\2\2f"+
		"i\3\2\2\2ge\3\2\2\2hj\t\2\2\2ih\3\2\2\2ij\3\2\2\2j\3\3\2\2\2k\u00c5\5"+
		"\6\4\2ln\5\6\4\2ml\3\2\2\2mn\3\2\2\2no\3\2\2\2o\u00c5\5\n\6\2pr\5\6\4"+
		"\2qp\3\2\2\2qr\3\2\2\2rs\3\2\2\2s\u00c5\5\b\5\2tv\5\6\4\2ut\3\2\2\2uv"+
		"\3\2\2\2vw\3\2\2\2w\u00c5\5\f\7\2xz\5\6\4\2yx\3\2\2\2yz\3\2\2\2z|\3\2"+
		"\2\2{}\t\2\2\2|{\3\2\2\2|}\3\2\2\2}~\3\2\2\2~\u00c5\5\64\33\2\177\u0081"+
		"\5\6\4\2\u0080\177\3\2\2\2\u0080\u0081\3\2\2\2\u0081\u0083\3\2\2\2\u0082"+
		"\u0084\t\2\2\2\u0083\u0082\3\2\2\2\u0083\u0084\3\2\2\2\u0084\u0085\3\2"+
		"\2\2\u0085\u0087\5\32\16\2\u0086\u0088\t\2\2\2\u0087\u0086\3\2\2\2\u0087"+
		"\u0088\3\2\2\2\u0088\u0089\3\2\2\2\u0089\u008b\7\7\2\2\u008a\u008c\t\2"+
		"\2\2\u008b\u008a\3\2\2\2\u008b\u008c\3\2\2\2\u008c\u008d\3\2\2\2\u008d"+
		"\u008e\7\31\2\2\u008e\u008f\5\20\t\2\u008f\u0090\7\32\2\2\u0090\u00c5"+
		"\3\2\2\2\u0091\u0093\5\6\4\2\u0092\u0091\3\2\2\2\u0092\u0093\3\2\2\2\u0093"+
		"\u0095\3\2\2\2\u0094\u0096\t\2\2\2\u0095\u0094\3\2\2\2\u0095\u0096\3\2"+
		"\2\2\u0096\u0097\3\2\2\2\u0097\u0099\5\32\16\2\u0098\u009a\t\2\2\2\u0099"+
		"\u0098\3\2\2\2\u0099\u009a\3\2\2\2\u009a\u009b\3\2\2\2\u009b\u009d\7\7"+
		"\2\2\u009c\u009e\t\2\2\2\u009d\u009c\3\2\2\2\u009d\u009e\3\2\2\2\u009e"+
		"\u009f\3\2\2\2\u009f\u00a0\7\31\2\2\u00a0\u00a1\5\24\13\2\u00a1\u00a2"+
		"\7\32\2\2\u00a2\u00c5\3\2\2\2\u00a3\u00a5\5\6\4\2\u00a4\u00a3\3\2\2\2"+
		"\u00a4\u00a5\3\2\2\2\u00a5\u00a7\3\2\2\2\u00a6\u00a8\t\2\2\2\u00a7\u00a6"+
		"\3\2\2\2\u00a7\u00a8\3\2\2\2\u00a8\u00a9\3\2\2\2\u00a9\u00ab\5\32\16\2"+
		"\u00aa\u00ac\t\2\2\2\u00ab\u00aa\3\2\2\2\u00ab\u00ac\3\2\2\2\u00ac\u00ad"+
		"\3\2\2\2\u00ad\u00af\7\7\2\2\u00ae\u00b0\t\2\2\2\u00af\u00ae\3\2\2\2\u00af"+
		"\u00b0\3\2\2\2\u00b0\u00b1\3\2\2\2\u00b1\u00b2\5$\23\2\u00b2\u00c5\3\2"+
		"\2\2\u00b3\u00b5\5\6\4\2\u00b4\u00b3\3\2\2\2\u00b4\u00b5\3\2\2\2\u00b5"+
		"\u00b7\3\2\2\2\u00b6\u00b8\t\2\2\2\u00b7\u00b6\3\2\2\2\u00b7\u00b8\3\2"+
		"\2\2\u00b8\u00b9\3\2\2\2\u00b9\u00c2\5\26\f\2\u00ba\u00bc\t\2\2\2\u00bb"+
		"\u00ba\3\2\2\2\u00bb\u00bc\3\2\2\2\u00bc\u00bd\3\2\2\2\u00bd\u00bf\7\7"+
		"\2\2\u00be\u00c0\t\2\2\2\u00bf\u00be\3\2\2\2\u00bf\u00c0\3\2\2\2\u00c0"+
		"\u00c1\3\2\2\2\u00c1\u00c3\5\64\33\2\u00c2\u00bb\3\2\2\2\u00c2\u00c3\3"+
		"\2\2\2\u00c3\u00c5\3\2\2\2\u00c4k\3\2\2\2\u00c4m\3\2\2\2\u00c4q\3\2\2"+
		"\2\u00c4u\3\2\2\2\u00c4y\3\2\2\2\u00c4\u0080\3\2\2\2\u00c4\u0092\3\2\2"+
		"\2\u00c4\u00a4\3\2\2\2\u00c4\u00b4\3\2\2\2\u00c5\5\3\2\2\2\u00c6\u00cf"+
		"\7\f\2\2\u00c7\u00cb\7\13\2\2\u00c8\u00ca\7\13\2\2\u00c9\u00c8\3\2\2\2"+
		"\u00ca\u00cd\3\2\2\2\u00cb\u00c9\3\2\2\2\u00cb\u00cc\3\2\2\2\u00cc\u00cf"+
		"\3\2\2\2\u00cd\u00cb\3\2\2\2\u00ce\u00c6\3\2\2\2\u00ce\u00c7\3\2\2\2\u00cf"+
		"\7\3\2\2\2\u00d0\u00d1\7\r\2\2\u00d1\u00ea\5\32\16\2\u00d2\u00d3\7\r\2"+
		"\2\u00d3\u00d5\5\32\16\2\u00d4\u00d6\t\2\2\2\u00d5\u00d4\3\2\2\2\u00d5"+
		"\u00d6\3\2\2\2\u00d6\u00d7\3\2\2\2\u00d7\u00dc\7E\2\2\u00d8\u00d9\7$\2"+
		"\2\u00d9\u00db\7E\2\2\u00da\u00d8\3\2\2\2\u00db\u00de\3\2\2\2\u00dc\u00da"+
		"\3\2\2\2\u00dc\u00dd\3\2\2\2\u00dd\u00e7\3\2\2\2\u00de\u00dc\3\2\2\2\u00df"+
		"\u00e1\t\2\2\2\u00e0\u00df\3\2\2\2\u00e0\u00e1\3\2\2\2\u00e1\u00e2\3\2"+
		"\2\2\u00e2\u00e4\7 \2\2\u00e3\u00e5\t\2\2\2\u00e4\u00e3\3\2\2\2\u00e4"+
		"\u00e5\3\2\2\2\u00e5\u00e6\3\2\2\2\u00e6\u00e8\7E\2\2\u00e7\u00e0\3\2"+
		"\2\2\u00e7\u00e8\3\2\2\2\u00e8\u00ea\3\2\2\2\u00e9\u00d0\3\2\2\2\u00e9"+
		"\u00d2\3\2\2\2\u00ea\t\3\2\2\2\u00eb\u00ec\7\17\2\2\u00ec\u00f1\7E\2\2"+
		"\u00ed\u00ee\7$\2\2\u00ee\u00f0\7E\2\2\u00ef\u00ed\3\2\2\2\u00f0\u00f3"+
		"\3\2\2\2\u00f1\u00ef\3\2\2\2\u00f1\u00f2\3\2\2\2\u00f2\u00f4\3\2\2\2\u00f3"+
		"\u00f1\3\2\2\2\u00f4\u00f5\7$\2\2\u00f5\u010c\7\61\2\2\u00f6\u00f7\7\17"+
		"\2\2\u00f7\u00fc\7E\2\2\u00f8\u00f9\7$\2\2\u00f9\u00fb\7E\2\2\u00fa\u00f8"+
		"\3\2\2\2\u00fb\u00fe\3\2\2\2\u00fc\u00fa\3\2\2\2\u00fc\u00fd\3\2\2\2\u00fd"+
		"\u00ff\3\2\2\2\u00fe\u00fc\3\2\2\2\u00ff\u0100\7$\2\2\u0100\u0109\5\32"+
		"\16\2\u0101\u0103\t\2\2\2\u0102\u0101\3\2\2\2\u0102\u0103\3\2\2\2\u0103"+
		"\u0104\3\2\2\2\u0104\u0106\7 \2\2\u0105\u0107\t\2\2\2\u0106\u0105\3\2"+
		"\2\2\u0106\u0107\3\2\2\2\u0107\u0108\3\2\2\2\u0108\u010a\7E\2\2\u0109"+
		"\u0102\3\2\2\2\u0109\u010a\3\2\2\2\u010a\u010c\3\2\2\2\u010b\u00eb\3\2"+
		"\2\2\u010b\u00f6\3\2\2\2\u010c\13\3\2\2\2\u010d\u010e\7\21\2\2\u010e\u010f"+
		"\5\32\16\2\u010f\r\3\2\2\2\u0110\u0112\5\34\17\2\u0111\u0113\t\2\2\2\u0112"+
		"\u0111\3\2\2\2\u0112\u0113\3\2\2\2\u0113\u0114\3\2\2\2\u0114\u0116\7!"+
		"\2\2\u0115\u0117\t\2\2\2\u0116\u0115\3\2\2\2\u0116\u0117\3\2\2\2\u0117"+
		"\u0118\3\2\2\2\u0118\u0119\5\32\16\2\u0119\17\3\2\2\2\u011a\u0125\5\16"+
		"\b\2\u011b\u011d\t\2\2\2\u011c\u011b\3\2\2\2\u011c\u011d\3\2\2\2\u011d"+
		"\u011e\3\2\2\2\u011e\u0120\7#\2\2\u011f\u0121\t\2\2\2\u0120\u011f\3\2"+
		"\2\2\u0120\u0121\3\2\2\2\u0121\u0122\3\2\2\2\u0122\u0124\5\16\b\2\u0123"+
		"\u011c\3\2\2\2\u0124\u0127\3\2\2\2\u0125\u0123\3\2\2\2\u0125\u0126\3\2"+
		"\2\2\u0126\21\3\2\2\2\u0127\u0125\3\2\2\2\u0128\u012a\5\34\17\2\u0129"+
		"\u012b\t\2\2\2\u012a\u0129\3\2\2\2\u012a\u012b\3\2\2\2\u012b\u012c\3\2"+
		"\2\2\u012c\u012e\7\3\2\2\u012d\u012f\t\2\2\2\u012e\u012d\3\2\2\2\u012e"+
		"\u012f\3\2\2\2\u012f\u0130\3\2\2\2\u0130\u0131\5\34\17\2\u0131\23\3\2"+
		"\2\2\u0132\u013d\5\22\n\2\u0133\u0135\t\2\2\2\u0134\u0133\3\2\2\2\u0134"+
		"\u0135\3\2\2\2\u0135\u0136\3\2\2\2\u0136\u0138\7#\2\2\u0137\u0139\t\2"+
		"\2\2\u0138\u0137\3\2\2\2\u0138\u0139\3\2\2\2\u0139\u013a\3\2\2\2\u013a"+
		"\u013c\5\22\n\2\u013b\u0134\3\2\2\2\u013c\u013f\3\2\2\2\u013d\u013b\3"+
		"\2\2\2\u013d\u013e\3\2\2\2\u013e\25\3\2\2\2\u013f\u013d\3\2\2\2\u0140"+
		"\u0145\5\32\16\2\u0141\u0142\7\31\2\2\u0142\u0143\5\20\t\2\u0143\u0144"+
		"\7\32\2\2\u0144\u0146\3\2\2\2\u0145\u0141\3\2\2\2\u0145\u0146\3\2\2\2"+
		"\u0146\u014f\3\2\2\2\u0147\u0149\t\2\2\2\u0148\u0147\3\2\2\2\u0148\u0149"+
		"\3\2\2\2\u0149\u014a\3\2\2\2\u014a\u014c\7!\2\2\u014b\u014d\t\2\2\2\u014c"+
		"\u014b\3\2\2\2\u014c\u014d\3\2\2\2\u014d\u014e\3\2\2\2\u014e\u0150\5\32"+
		"\16\2\u014f\u0148\3\2\2\2\u014f\u0150\3\2\2\2\u0150\27\3\2\2\2\u0151\u0152"+
		"\t\3\2\2\u0152\31\3\2\2\2\u0153\u0155\7E\2\2\u0154\u0156\5\30\r\2\u0155"+
		"\u0154\3\2\2\2\u0155\u0156\3\2\2\2\u0156\u015c\3\2\2\2\u0157\u0158\7\35"+
		"\2\2\u0158\u0159\5\32\16\2\u0159\u015a\7\36\2\2\u015a\u015c\3\2\2\2\u015b"+
		"\u0153\3\2\2\2\u015b\u0157\3\2\2\2\u015c\33\3\2\2\2\u015d\u015e\b\17\1"+
		"\2\u015e\u015f\7E\2\2\u015f\u0165\3\2\2\2\u0160\u0161\f\3\2\2\u0161\u0162"+
		"\7$\2\2\u0162\u0164\7E\2\2\u0163\u0160\3\2\2\2\u0164\u0167\3\2\2\2\u0165"+
		"\u0163\3\2\2\2\u0165\u0166\3\2\2\2\u0166\35\3\2\2\2\u0167\u0165\3\2\2"+
		"\2\u0168\u016a\7\6\2\2\u0169\u016b\5\34\17\2\u016a\u0169\3\2\2\2\u016a"+
		"\u016b\3\2\2\2\u016b\u0191\3\2\2\2\u016c\u016d\7\6\2\2\u016d\u016e\7\33"+
		"\2\2\u016e\u0179\5\34\17\2\u016f\u0171\7\27\2\2\u0170\u016f\3\2\2\2\u0170"+
		"\u0171\3\2\2\2\u0171\u0172\3\2\2\2\u0172\u0174\7#\2\2\u0173\u0175\7\27"+
		"\2\2\u0174\u0173\3\2\2\2\u0174\u0175\3\2\2\2\u0175\u0176\3\2\2\2\u0176"+
		"\u0178\5\34\17\2\u0177\u0170\3\2\2\2\u0178\u017b\3\2\2\2\u0179\u0177\3"+
		"\2\2\2\u0179\u017a\3\2\2\2\u017a\u017c\3\2\2\2\u017b\u0179\3\2\2\2\u017c"+
		"\u017d\7\34\2\2\u017d\u0191\3\2\2\2\u017e\u017f\7\6\2\2\u017f\u0180\7"+
		"\31\2\2\u0180\u018b\5\34\17\2\u0181\u0183\7\27\2\2\u0182\u0181\3\2\2\2"+
		"\u0182\u0183\3\2\2\2\u0183\u0184\3\2\2\2\u0184\u0186\7#\2\2\u0185\u0187"+
		"\7\27\2\2\u0186\u0185\3\2\2\2\u0186\u0187\3\2\2\2\u0187\u0188\3\2\2\2"+
		"\u0188\u018a\5\34\17\2\u0189\u0182\3\2\2\2\u018a\u018d\3\2\2\2\u018b\u0189"+
		"\3\2\2\2\u018b\u018c\3\2\2\2\u018c\u018e\3\2\2\2\u018d\u018b\3\2\2\2\u018e"+
		"\u018f\7\32\2\2\u018f\u0191\3\2\2\2\u0190\u0168\3\2\2\2\u0190\u016c\3"+
		"\2\2\2\u0190\u017e\3\2\2\2\u0191\37\3\2\2\2\u0192\u01ad\5\66\34\2\u0193"+
		"\u01ad\58\35\2\u0194\u01ad\5:\36\2\u0195\u01ad\5<\37\2\u0196\u01ad\5>"+
		" \2\u0197\u01ad\5@!\2\u0198\u01ad\5B\"\2\u0199\u01ad\5D#\2\u019a\u01ad"+
		"\5F$\2\u019b\u019c\7\35\2\2\u019c\u01a7\5 \21\2\u019d\u019f\7\27\2\2\u019e"+
		"\u019d\3\2\2\2\u019e\u019f\3\2\2\2\u019f\u01a0\3\2\2\2\u01a0\u01a2\7#"+
		"\2\2\u01a1\u01a3\7\27\2\2\u01a2\u01a1\3\2\2\2\u01a2\u01a3\3\2\2\2\u01a3"+
		"\u01a4\3\2\2\2\u01a4\u01a6\5 \21\2\u01a5\u019e\3\2\2\2\u01a6\u01a9\3\2"+
		"\2\2\u01a7\u01a5\3\2\2\2\u01a7\u01a8\3\2\2\2\u01a8\u01aa\3\2\2\2\u01a9"+
		"\u01a7\3\2\2\2\u01aa\u01ab\7\36\2\2\u01ab\u01ad\3\2\2\2\u01ac\u0192\3"+
		"\2\2\2\u01ac\u0193\3\2\2\2\u01ac\u0194\3\2\2\2\u01ac\u0195\3\2\2\2\u01ac"+
		"\u0196\3\2\2\2\u01ac\u0197\3\2\2\2\u01ac\u0198\3\2\2\2\u01ac\u0199\3\2"+
		"\2\2\u01ac\u019a\3\2\2\2\u01ac\u019b\3\2\2\2\u01ad!\3\2\2\2\u01ae\u01b0"+
		"\n\4\2\2\u01af\u01ae\3\2\2\2\u01b0\u01b3\3\2\2\2\u01b1\u01af\3\2\2\2\u01b1"+
		"\u01b2\3\2\2\2\u01b2#\3\2\2\2\u01b3\u01b1\3\2\2\2\u01b4\u01b5\7C\2\2\u01b5"+
		"\u01b6\5\"\22\2\u01b6\u01b7\7D\2\2\u01b7%\3\2\2\2\u01b8\u01d0\5.\30\2"+
		"\u01b9\u01d0\5\36\20\2\u01ba\u01bb\5\34\17\2\u01bb\u01bc\5\36\20\2\u01bc"+
		"\u01d0\3\2\2\2\u01bd\u01bf\5\34\17\2\u01be\u01c0\t\2\2\2\u01bf\u01be\3"+
		"\2\2\2\u01bf\u01c0\3\2\2\2\u01c0\u01c1\3\2\2\2\u01c1\u01c3\7 \2\2\u01c2"+
		"\u01c4\t\2\2\2\u01c3\u01c2\3\2\2\2\u01c3\u01c4\3\2\2\2\u01c4\u01c5\3\2"+
		"\2\2\u01c5\u01c7\5.\30\2\u01c6\u01c8\5\36\20\2\u01c7\u01c6\3\2\2\2\u01c7"+
		"\u01c8\3\2\2\2\u01c8\u01d0\3\2\2\2\u01c9\u01ca\5\34\17\2\u01ca\u01cb\5"+
		"P)\2\u01cb\u01cd\5.\30\2\u01cc\u01ce\5\36\20\2\u01cd\u01cc\3\2\2\2\u01cd"+
		"\u01ce\3\2\2\2\u01ce\u01d0\3\2\2\2\u01cf\u01b8\3\2\2\2\u01cf\u01b9\3\2"+
		"\2\2\u01cf\u01ba\3\2\2\2\u01cf\u01bd\3\2\2\2\u01cf\u01c9\3\2\2\2\u01d0"+
		"\'\3\2\2\2\u01d1\u01d2\7\31\2\2\u01d2\u01e5\7\32\2\2\u01d3\u01d4\7\31"+
		"\2\2\u01d4\u01df\5&\24\2\u01d5\u01d7\t\2\2\2\u01d6\u01d5\3\2\2\2\u01d6"+
		"\u01d7\3\2\2\2\u01d7\u01d8\3\2\2\2\u01d8\u01da\7#\2\2\u01d9\u01db\t\2"+
		"\2\2\u01da\u01d9\3\2\2\2\u01da\u01db\3\2\2\2\u01db\u01dc\3\2\2\2\u01dc"+
		"\u01de\5&\24\2\u01dd\u01d6\3\2\2\2\u01de\u01e1\3\2\2\2\u01df\u01dd\3\2"+
		"\2\2\u01df\u01e0\3\2\2\2\u01e0\u01e2\3\2\2\2\u01e1\u01df\3\2\2\2\u01e2"+
		"\u01e3\7\32\2\2\u01e3\u01e5\3\2\2\2\u01e4\u01d1\3\2\2\2\u01e4\u01d3\3"+
		"\2\2\2\u01e5)\3\2\2\2\u01e6\u01e7\b\26\1\2\u01e7\u01ee\5 \21\2\u01e8\u01ee"+
		"\5\34\17\2\u01e9\u01ee\5(\25\2\u01ea\u01eb\5\34\17\2\u01eb\u01ec\5(\25"+
		"\2\u01ec\u01ee\3\2\2\2\u01ed\u01e6\3\2\2\2\u01ed\u01e8\3\2\2\2\u01ed\u01e9"+
		"\3\2\2\2\u01ed\u01ea\3\2\2\2\u01ee\u01fa\3\2\2\2\u01ef\u01f1\f\3\2\2\u01f0"+
		"\u01f2\t\2\2\2\u01f1\u01f0\3\2\2\2\u01f1\u01f2\3\2\2\2\u01f2\u01f3\3\2"+
		"\2\2\u01f3\u01f5\7$\2\2\u01f4\u01f6\t\2\2\2\u01f5\u01f4\3\2\2\2\u01f5"+
		"\u01f6\3\2\2\2\u01f6\u01f7\3\2\2\2\u01f7\u01f9\5*\26\4\u01f8\u01ef\3\2"+
		"\2\2\u01f9\u01fc\3\2\2\2\u01fa\u01f8\3\2\2\2\u01fa\u01fb\3\2\2\2\u01fb"+
		"+\3\2\2\2\u01fc\u01fa\3\2\2\2\u01fd\u0217\5*\26\2\u01fe\u01ff\5*\26\2"+
		"\u01ff\u0201\7\35\2\2\u0200\u0202\5:\36\2\u0201\u0200\3\2\2\2\u0201\u0202"+
		"\3\2\2\2\u0202\u0204\3\2\2\2\u0203\u0205\t\2\2\2\u0204\u0203\3\2\2\2\u0204"+
		"\u0205\3\2\2\2\u0205\u0207\3\2\2\2\u0206\u0208\7!\2\2\u0207\u0206\3\2"+
		"\2\2\u0207\u0208\3\2\2\2\u0208\u020a\3\2\2\2\u0209\u020b\t\2\2\2\u020a"+
		"\u0209\3\2\2\2\u020a\u020b\3\2\2\2\u020b\u020d\3\2\2\2\u020c\u020e\5:"+
		"\36\2\u020d\u020c\3\2\2\2\u020d\u020e\3\2\2\2\u020e\u020f\3\2\2\2\u020f"+
		"\u0210\7\36\2\2\u0210\u0217\3\2\2\2\u0211\u0212\5*\26\2\u0212\u0213\7"+
		"\35\2\2\u0213\u0214\5*\26\2\u0214\u0215\7\36\2\2\u0215\u0217\3\2\2\2\u0216"+
		"\u01fd\3\2\2\2\u0216\u01fe\3\2\2\2\u0216\u0211\3\2\2\2\u0217-\3\2\2\2"+
		"\u0218\u0219\b\30\1\2\u0219\u0221\5,\27\2\u021a\u021b\7\31\2\2\u021b\u021c"+
		"\5.\30\2\u021c\u021d\7\32\2\2\u021d\u0221\3\2\2\2\u021e\u021f\7/\2\2\u021f"+
		"\u0221\5.\30\6\u0220\u0218\3\2\2\2\u0220\u021a\3\2\2\2\u0220\u021e\3\2"+
		"\2\2\u0221\u023f\3\2\2\2\u0222\u0224\f\5\2\2\u0223\u0225\t\2\2\2\u0224"+
		"\u0223\3\2\2\2\u0224\u0225\3\2\2\2\u0225\u0226\3\2\2\2\u0226\u0228\t\5"+
		"\2\2\u0227\u0229\t\2\2\2\u0228\u0227\3\2\2\2\u0228\u0229\3\2\2\2\u0229"+
		"\u022a\3\2\2\2\u022a\u023e\5.\30\6\u022b\u022d\f\4\2\2\u022c\u022e\t\2"+
		"\2\2\u022d\u022c\3\2\2\2\u022d\u022e\3\2\2\2\u022e\u022f\3\2\2\2\u022f"+
		"\u0231\t\6\2\2\u0230\u0232\t\2\2\2\u0231\u0230\3\2\2\2\u0231\u0232\3\2"+
		"\2\2\u0232\u0233\3\2\2\2\u0233\u023e\5.\30\5\u0234\u0236\f\3\2\2\u0235"+
		"\u0237\t\2\2\2\u0236\u0235\3\2\2\2\u0236\u0237\3\2\2\2\u0237\u0238\3\2"+
		"\2\2\u0238\u023a\t\7\2\2\u0239\u023b\t\2\2\2\u023a\u0239\3\2\2\2\u023a"+
		"\u023b\3\2\2\2\u023b\u023c\3\2\2\2\u023c\u023e\5.\30\4\u023d\u0222\3\2"+
		"\2\2\u023d\u022b\3\2\2\2\u023d\u0234\3\2\2\2\u023e\u0241\3\2\2\2\u023f"+
		"\u023d\3\2\2\2\u023f\u0240\3\2\2\2\u0240/\3\2\2\2\u0241\u023f\3\2\2\2"+
		"\u0242\u0248\5.\30\2\u0243\u0244\5.\30\2\u0244\u0245\5P)\2\u0245\u0246"+
		"\5.\30\2\u0246\u0248\3\2\2\2\u0247\u0242\3\2\2\2\u0247\u0243\3\2\2\2\u0248"+
		"\61\3\2\2\2\u0249\u024a\b\32\1\2\u024a\u024c\5\60\31\2\u024b\u024d\7\27"+
		"\2\2\u024c\u024b\3\2\2\2\u024c\u024d\3\2\2\2\u024d\u024f\3\2\2\2\u024e"+
		"\u0250\5\36\20\2\u024f\u024e\3\2\2\2\u024f\u0250\3\2\2\2\u0250\u0257\3"+
		"\2\2\2\u0251\u0253\7\65\2\2\u0252\u0254\7\27\2\2\u0253\u0252\3\2\2\2\u0253"+
		"\u0254\3\2\2\2\u0254\u0255\3\2\2\2\u0255\u0257\5\62\32\4\u0256\u0249\3"+
		"\2\2\2\u0256\u0251\3\2\2\2\u0257\u025e\3\2\2\2\u0258\u0259\f\3\2\2\u0259"+
		"\u025a\5J&\2\u025a\u025b\5\62\32\4\u025b\u025d\3\2\2\2\u025c\u0258\3\2"+
		"\2\2\u025d\u0260\3\2\2\2\u025e\u025c\3\2\2\2\u025e\u025f\3\2\2\2\u025f"+
		"\63\3\2\2\2\u0260\u025e\3\2\2\2\u0261\u0267\5\62\32\2\u0262\u0263\5\62"+
		"\32\2\u0263\u0264\5L\'\2\u0264\u0265\5\64\33\2\u0265\u0267\3\2\2\2\u0266"+
		"\u0261\3\2\2\2\u0266\u0262\3\2\2\2\u0267\65\3\2\2\2\u0268\u0269\7\37\2"+
		"\2\u0269\67\3\2\2\2\u026a\u026b\7;\2\2\u026b9\3\2\2\2\u026c\u026d\7<\2"+
		"\2\u026d;\3\2\2\2\u026e\u026f\7=\2\2\u026f=\3\2\2\2\u0270\u0271\7>\2\2"+
		"\u0271?\3\2\2\2\u0272\u0273\7?\2\2\u0273A\3\2\2\2\u0274\u0275\7@\2\2\u0275"+
		"C\3\2\2\2\u0276\u0277\7A\2\2\u0277E\3\2\2\2\u0278\u0279\7B\2\2\u0279G"+
		"\3\2\2\2\u027a\u027b\t\b\2\2\u027bI\3\2\2\2\u027c\u027e\7\27\2\2\u027d"+
		"\u027c\3\2\2\2\u027d\u027e\3\2\2\2\u027e\u027f\3\2\2\2\u027f\u0281\5H"+
		"%\2\u0280\u0282\7\27\2\2\u0281\u0280\3\2\2\2\u0281\u0282\3\2\2\2\u0282"+
		"K\3\2\2\2\u0283\u0284\7\30\2\2\u0284\u0286\5H%\2\u0285\u0287\7\27\2\2"+
		"\u0286\u0285\3\2\2\2\u0286\u0287\3\2\2\2\u0287M\3\2\2\2\u0288\u0289\t"+
		"\t\2\2\u0289O\3\2\2\2\u028a\u028c\t\2\2\2\u028b\u028a\3\2\2\2\u028b\u028c"+
		"\3\2\2\2\u028c\u028d\3\2\2\2\u028d\u028f\5N(\2\u028e\u0290\t\2\2\2\u028f"+
		"\u028e\3\2\2\2\u028f\u0290\3\2\2\2\u0290Q\3\2\2\2rTZ_eimquy|\u0080\u0083"+
		"\u0087\u008b\u0092\u0095\u0099\u009d\u00a4\u00a7\u00ab\u00af\u00b4\u00b7"+
		"\u00bb\u00bf\u00c2\u00c4\u00cb\u00ce\u00d5\u00dc\u00e0\u00e4\u00e7\u00e9"+
		"\u00f1\u00fc\u0102\u0106\u0109\u010b\u0112\u0116\u011c\u0120\u0125\u012a"+
		"\u012e\u0134\u0138\u013d\u0145\u0148\u014c\u014f\u0155\u015b\u0165\u016a"+
		"\u0170\u0174\u0179\u0182\u0186\u018b\u0190\u019e\u01a2\u01a7\u01ac\u01b1"+
		"\u01bf\u01c3\u01c7\u01cd\u01cf\u01d6\u01da\u01df\u01e4\u01ed\u01f1\u01f5"+
		"\u01fa\u0201\u0204\u0207\u020a\u020d\u0216\u0220\u0224\u0228\u022d\u0231"+
		"\u0236\u023a\u023d\u023f\u0247\u024c\u024f\u0253\u0256\u025e\u0266\u027d"+
		"\u0281\u0286\u028b\u028f";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}