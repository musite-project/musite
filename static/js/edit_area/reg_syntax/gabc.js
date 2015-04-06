editAreaLoader.load_syntax["gabc"] = {
	'DISPLAY_NAME' : 'GABC'
	,'COMMENT_SINGLE' : {1 : '%'}
	,'COMMENT_MULTI' : {}
	,'QUOTEMARKS' : ['"']
	,'KEYWORD_CASE_SENSITIVE' : true
	,'KEYWORDS' : {
		'attributes' : [
			'name','author','gabc-copyright',
			'score-copyright','office-part',
			'occasion','meter','commentary',
			'arranger','gabc-version','date',
			'manuscript','manuscript-reference',
			'manuscript-storage-place','book',
			'transcription-date','transcriber',
			'gregoriotex-font','mode','initial-style',
			'user-notes','annotation','generated-by',
			'style','virgula-position','number-of-voices'
		]
	}
	,'OPERATORS' :[
		':', ';'
	]
	,'DELIMITERS' :[
		'{', '}'
	]
	,'REGEXPS' : {
		'tags' : {
			'search' : '()(</?[a-z][^ \r\n\t>]*[^>]*>)()'
			,'class' : 'tags'
			,'modifiers' : 'gi'
			,'execute' : 'before' // before or after
		}
		,'notes' : {
			'search' : '()(\\([^\\)]*\\))()'
			,'class' : 'notes'
			,'modifiers' : 'gi'
			,'execute' : 'before' // before or after
		}
		,'traduction' : {
			'search' : '()(\\[[^\\]]*\\])()'
			,'class' : 'traduction'
			,'modifiers' : 'gi'
			,'execute' : 'before' // before or after
		}
		,'attributes' : {
			'search' : '( |\n|\r|\t)([^ \r\n\t=]+)(=)'
			,'class' : 'attributes'
			,'modifiers' : 'g'
			,'execute' : 'before' // before or after
		}
	}
	,'STYLES' : {
		'COMMENTS': 'color: #AAAAAA;'
		,'QUOTESMARKS': 'color: #6381F8;'
		,'KEYWORDS' : {
			'attributes': 'color: #5882FA;'
			,'values' : 'color: #2B60FF;'
			,'specials' : 'color: #FF0000;'
			}
		,'OPERATORS' : 'color: #0040FF;'
		,'DELIMITERS' : 'color: #FF00FF;'
		,'REGEXPS' : {
			'notes': 'color: #B18904;'
			,'traduction': 'color: #5FB404;'
			,'tags': 'color: #B40404;'
		}
				
	}
};
