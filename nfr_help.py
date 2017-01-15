def suffix(words, s):
    return ' '.join(e+s for e in words.split())

class Keywords(object):
    def __init__(self):
        # config_commands
        self.db         = '-db -d --database(-d)'
        #self.dbFollow   = suffix(self.db,'f')+' '+suffix(self.db,'-follow')
        self.cls        = '-cls --clear(-cls)'
        self.exit       = '-q --quit(-q)'
        self.wordnetDl  = '--wordnet-download'
        self.wordnetOn  = '-w+ --use-wordnet(-w+)'
        self.wordnetOff = '-w- --ignore-wordnet-(-w-)'
        self.wordnetInfo= '-w? --wordnet-info(-w?)'
        self.website    = '--sourcecode --website'
        self.chdir      = '-cd --change-working-directory(-cd) -chdir -cwd'
        # global_commands
        self.refresh    = '* ** -all -all-untagged' # heal? remove: all-untagged!
        self.heal       = '-heal'
        # help_commands
        self.help       = '-h -help --help(-h)'
        # subselection_commands
        self.fix        = '-find --find-missing-files(-find)'
        #self.fixByName  = suffix(self.fix,'-by-name')
        self.lost       = '-lost -missing'
        self.detach     = '-detach -displace'
        self.remove     = '-remove'
        self.t          = '-t' # UGLY
        self.p          = '-p' # UGLY
        self.copy       = '-copy --copy-files(-copy)'
        self.copyFollow = '-copy-follow --copy-files-&-update-link(-copy-follow)'
        self.move       = '-mv --move(-mv)'
        self.RMDF       = '-RMDF --REMOVE-DUPLICATE-FILES(-RMDF)'
        self.RMDFx      = suffix(self.RMDF,'!') # permanent remove
        self.alias      = '-a --alias(-a)'
        self.aliasOff   = '-raw '+suffix(self.alias,'-')
        self.aliasRemove= '-rma -alias-remove(-rma)'
        self.idea       = '-i -idea -text -note -write'
        self.rename     = '-r --rename-tag(-r)'
        self.renameMatchingGroup = '-rg --rename-matching-tag--group(-rg)'
        self.renameMatchingWhole = '-ra --rename-matching-tag--whole(-ra)'
        self.list       = '-l --list(-l)'
        self.listMore   = suffix(self.list,'+')
        self.listMore2  = suffix(self.list,'++')
        self.listLess   = suffix(self.list,'-')
        self.dir        = '-dir --directory-distribution(-dir)'
        self.present    = '-present -found'
        self.edit       = '-e --edit-tags(-e)'
        self.over       = '-> -t> -tags> -over'
        self.less       = '-< -t< -tags< -less'
        self.equal      = '-= -t= -tags= -equal'
        self.inverse    = '-inv --inverse-selection(-inv)'
        self.c          = '-c -copy-filepath(-c)'
        self.open       = '-o -open'
        self.browse     = '-b --browse-directory(-b)'
        self.cfg        = '-cfg -ini -configure -config'
        self.count      = '-? --count-tags(-?)'
        self.rawCopy    = '-c: -copy:'
        self.local      = '-local -files'
        self.remote     = '-remote'
        self.links      = '-links'
        self.ideas      = '-ideas -texts'
        self.ct         = '-ct --copy-tags(-ct)'
        self.ctSplit    = '-cts '+suffix(self.ct,'+')+' '+suffix(self.ct,'-split') # long format
        self.makeFilelist = '-make-filelist'
        self.x          = '-x -run'
        self.ch         = '-ch -copy-hash(-ch)'
        self.cm         = '-cm -copy-metadata(-cm)'
        self.rehash     = '-rehash --rehash'
        self.color      = '-color -colour -tint'
        self.intersection = '-int -intersect -intersection'
        self.difference = '-diff -difference -orphaned'
        self.rare       = '-rare -uncommon'
        self.similar    = '-sim --similarity-search(-sim)'
        self.pSimilar   = '-simp --similarity-search--perceptual(-simp)'
        self.similarFuz = '-simf --similarity-search--fuzzy(-simf)'
        self.pSimilarFuz= '-simpf --similarity-search--perceptual+fuzzy(-simpf) -simfp'
        self.reduceNot  = '-reduce-not --reduce-not'
        self.memSave    = '-m< -mem-save -mem< -save -memorize'
        self.memLoad    = '-m> -mem-load -mem> -load -recall'
        self.memList    = '-m -mem-list -mem'
        self.addModeNew = '+++'
        self.subModeNew = '---'
        self.defModeNew = '==='
        self.addMode    = '++'
        self.subMode    = '--'
        self.defMode    = '=='
        self.script     = '-script --script'
        self.autoDl     = '-dl+ --auto-download-on(-dl+)'
        self.autoDlOff  = '-dl- --auto-download-off(-dl-)'
        self.group      = '-g --group-variants(-g) -group'
        self.ungroup    = '-g- --ungroup-variants(-g-) -group-'
        self.variants   = '-v --variants(-v)'
        self.variantsAdd= '-v+ --variants-add(-v+)'
        self.variantsSub= '-v- --variants-subtract(-v-)'
        self.addByHash  = '-# -hash'
        self.export     = '-export --export'
        self.subselect  = '-s -sub-select -slice'
        self.match      = '-m --match-substring-sub-select(-m)'
        self.about      = '-about --about -version --version'
        self.sort       = '-sort --sort'
        self.reverse    = '-rev -reverse'
        self.shuffle    = '-shuffle --shuffle'
        self.motd       = '-motd --message-of-the-day(-motd)'
        self.runClipboard = '-xc --execute-clipboard(-xc)'
        self.makeCollage= '-collage'
        self.iterClipboard = '-ic --iterate-clipboard(-ic)'
        self.clipb2img  = '-c2i --clipboard2image(-c2i)'
        self.delay      = '-delay --delay'
        #self.exportSearch = '-export-search'
        #self.exportSelection = '-export-selection'
        
    def make(self):
        attrs = [ attr for attr in dir(self) if not callable(attr) and not attr.startswith('__') and not attr in ('make','cpl','aliases') ]
        for attr in attrs: # parse and convert all to tuples
            words = getattr(self, attr)
            if isinstance(words, basestring):
                setattr(self, attr, tuple(filter(None,words.split())))
        self.__all__ = ( getattr(self, attr) for attr in attrs ) # get lists of words
        self.__all__ = tuple( item for subseq in self.__all__ for item in subseq ) # flattens list
    def cpl(self, attrs=None):
        if attrs:
            words = ( getattr(self, attr.replace('kw.','')) for attr in attrs.split() )
            return tuple( item for subseq in words for item in subseq ) # flattens list
        return self.__all__
    def aliases(self, word):
        labels = [ attr for attr in dir(self) if not callable(attr) and not attr.startswith('__') and not attr in ('make','cpl','aliases') ]
        for label in labels:
            aliases = getattr(self, label)#.split()
            if word in aliases:
                return aliases
        return None

kw = Keywords() # in string format (make() to create tuples)

def usage(kw, s): # input: space delimited string
    if len(kw.split()) > 1:
        kws = ('**'+e+'**' for e in kw.split())
        return '\n ('+'|'.join(kws)+') '+s
    else:
        return '\n **'+kws+'** '+s

def usage2(kw, s, trimPadding=False): # input: space delimited string
    if trimPadding and '\n' in s:
        s = '\n'.join(map(str.strip, s.split('\n')))
    if len(kw) > 1:
        kws = ('**'+e+'**' for e in kw)
        if trimPadding:
            return '('+'|'.join(kws)+')'+s
        else:
            return '('+'|'.join(kws)+')'+s
    else:
        return '**'+kws+'**'+s

paragraph_kw = ''
def set_paragraph(kw):
    global paragraph_kw
    paragraph_kw = kw
    return kw
def get_paragraph():
    global paragraph_kw
    return paragraph_kw
PARA = set_paragraph
pkw  = get_paragraph

help = [
 (kw.db, usage(kw.db, '[<database/folder>]')+
 '''
 Creates or opens an existing database.
 '''),
 (PARA('tagging tag tags adding file files'),'''
--------------------------------------------------------------------------------
# *Tagging: files*
--------------------------------------------------------------------------------

 *<filepath>*
 Adds & selects file for tagging (press enter to end tagging-mode).

 *<directory>*
 Adds & selects all files in the directory.
 '''),
 (PARA('tagging adding tags tag'),'''
--------------------------------------------------------------------------------
# *Tag operations on selected file(s)*
--------------------------------------------------------------------------------
 '''),
 (kw.edit+' '+pkw(),'''
 + Manual tag editing.

    (**-e**|**-edit**) <tag1> <tag2> <tag3>
    Adds tags (for all items in current selection).

    (**-e**|**-edit**) `-` <tag1> <tag2>
    Removes the two tags (from all items in current selection).

    (**-e**|**-edit**) `+` <tag2> `-` <tag3>
    *Adds* and *removes* a tag (all items in current selection).
 '''),
 (kw.rename+' rename remove delete '+pkw(),'''
 + *Renaming* tags (in current selection).

    (**-r**|**-rename**) <old-tag> <new-tag>
    Also removes tag if <new-tag> is not specified.
'''),
 (kw.rename+' rename remove delete '+pkw(),'''
 + *Removing* tags (from current selection).

    (**-r**|**-rename**) <tag-to-remove>
    Renaming to none removes the tag.
 '''),
 (kw.renameMatchingGroup+' rename '+pkw(),'''
 + *Replaces* only the substring on match (in current selection).

    (**-rg**|**-rename-matching-group**) <search-string> <replacement>
 '''),
 (kw.renameMatchingWhole+' rename remove delete '+pkw(),'''
 + *Renames* whole tag on substring match (in current selection).

    (**-ra**|**-rename-matching-whole**) <substring> <replace-whole-tag>
 '''),
 (kw.remove+' remove delete '+pkw(),'''
 + Removing selected file metadata from the database

    **-remove**
 '''),
 (PARA('idea text notes note'),'''
--------------------------------------------------------------------------------
# *Tagging: text* (aka "ideas")
--------------------------------------------------------------------------------
 '''),
 (kw.idea+' '+pkw(),'''
 (**-i**|**-idea**) <text>
 Adds a text/idea item.

 (**-i**|**-idea**)
 Searches for ideas (in current selection).

 Tip: Ideas can also be URL\'s. Useful if a file\'s data is changing.
 '''),
 (PARA('url links'),'''
--------------------------------------------------------------------------------
# *Tagging: remote URL\'s*
--------------------------------------------------------------------------------

 *<remote URL>*
 Adds a link for tagging (in a similar way to ideas).
 '''),
 (kw.links+' remote search '+pkw(),'''
 **-links**
 Searches for links (in current selection).
 '''),
 (kw.ideas+' idea ideas text search '+pkw(),'''
 **-ideas**
 Searches for ideas (in current selection).
 '''),
 (kw.remote+' idea ideas text search '+pkw(),'''
 **-remote**
 Searches for ideas and links (in current selection).
 '''),
 (PARA('selecting selection')),'''
--------------------------------------------------------------------------------
# *Selecting*
--------------------------------------------------------------------------------
 ''',
 ('* ** list listing show display info search '+pkw(),'''
 Type * or ** (additional hash-based file verification) for available tags.
 '''),
 '''
 The number of items selected is displayed inside the command prompt, ex: "{3}>"
 ''',
 (kw.list+' '+kw.listMore+' '+kw.listLess+' listing show display info '+pkw(),'''
 To display the selection list type (**-l**|**-list**) or (**-l+**|**-list+**) for more info.
 '''),
 '''
 + Selecting by tags and by index

    {0}> <tag1> <tag2> `-` <tag3>
    Selecting all items having tag1 and tag2 but not tag3.
 ''',
 ('-s : selection slice slices '+pkw(),'''
    {10}> **-s** <indexes>
    Selecting by list index, ex: "*2 3 4:7 8*" (without ").
 '''),
 ('| '+pkw(),'''
    + Joining selections

        {0}> <tag1> <tag2> `|` <tag1> <tag3>
        or just:
        {0}> <tag2> `|` <tag3> `*` <tag1>
        Joins the two search request results.
 '''),
 (PARA('file files'),'''
--------------------------------------------------------------------------------
# *Dealing with displaced/missing files*
--------------------------------------------------------------------------------
 '''),
 (kw.fix+' repair search '+pkw(),'''
 (**-fix**|**-find**) <directory/to/search/for/missing/files>
 Does a recursive search for missing database items based on their hashes.
 '''),
 (kw.lost+' broken search '+pkw(),'''
 (**-lost**|**-missing**)
 Searches for missing files (in current selection).
 '''),
 (PARA('listing displaying display show items file files'),'''
--------------------------------------------------------------------------------
# *Displaying search results*
--------------------------------------------------------------------------------
 '''),
 (kw.t+' list '+pkw(),'''
 **-t**
 Copies selected files into a temporary directory and opens it with a browser.
 After the browser is closed, the directory is removed.
 '''),
 (kw.open+' run '+pkw(),'''
 (**-o**|**-open**)
 Opens 1st item with the OS-default app.
 '''),
 (kw.open+' -x run '+pkw(),'''
 (**-o**|**-open**) [<indexes> **-x** <APPLICATION-FILEPATH>  [**-s** <indexes>]]
 Opens items based on index (of current selection) with a specified app.
 In case the index is not defined, the selection is: all the items.
 It appends the file list as a parameter for the executable.
 The optional -s is for aliases based on -o to use custom index selection.
 '''),
 (kw.browse+' location folder folders run '+pkw(),'''
 (**-b**|**-browse** [<index>|<filepath>])
 Opens the directory of a file if succeded by <index> or <filepath>.
 Opens location of the first intem in selection (if it exists).
 Opens database location upon empty selection and no parameters.
 '''),
 (PARA('multitasking multitask settings customization customisation'),'''
--------------------------------------------------------------------------------
# *Multitasking*
--------------------------------------------------------------------------------
 '''),
 ('; '+pkw(),'''
 Delimit commands by `;` to batch process (also as parameters).
 '''),
 (PARA('-a alias aliases multitasking multitask settings customization customisation'),'''
--------------------------------------------------------------------------------
# *Aliases*
--------------------------------------------------------------------------------
 '''),
 (kw.alias+' aliases '+pkw(),'''
 (**-a**|**-alias**) <alias> [<alias-extension>]
 Creates an alias for a custom command/text.

 + Defining

    (**-a**|**-alias**) *player* path/to/player.ext
    From now on, "*player*" will be substituted by "path/to/player.ext".

    # Some examples of usage:
    {0}> -a *player* path/to/player.ext
    {0}> -a *play* -o -x *player* -s
    {0}> retro music
    {7}> *play*
    or with index selection (-s):
    {7}> *play* 2:3 5

    {0}> -a -red -color red

 + Removing
 '''),
 (kw.alias+' '+kw.aliasRemove+' aliases '+pkw(),'''
    (**-rma**|**-alias-remove**) player
    Removes the alias "player" from the database.
 '''),
 '''
--------------------------------------------------------------------------------
# *Sub-Tags*
--------------------------------------------------------------------------------
 ''',
 (': '+pkw(),'''
 Every tag containing a `:` (delimits its parts) is a sub-tag.
 You can search for the whole sub-tag or its parts.
 Ex:
    animal`:`frog
    food`:`spaghetti
    undefined`:`
    `:`ugly_tag-name_hidden_from_sight
 '''),
 (PARA('file files'),'''
--------------------------------------------------------------------------------
# *File operations* <<<(be CAREFUL with these!)>>>
--------------------------------------------------------------------------------
 '''),
 (' '.join((kw.copy,kw.move))+' '+pkw(),'''
 [i] Files are renamed on filepath collision when moved or copied.
 '''),
 (kw.copy+' cp '+pkw(),'''
 **-copy** <destination/directory>
 '''),
 (kw.move+' mv '+pkw(),'''
 **-move** <destination/directory>
 '''),
 (kw.RMDF+' '+pkw(),'''
 (**-RMDF**|**-REMOVE-DUPLICATE-FILES**) <directory/to/process>
 '''),
 (PARA('other useful'),'''
--------------------------------------------------------------------------------
# *Other useful things*
--------------------------------------------------------------------------------
 '''),
 ('= _','''
 `=` <text1> `_` <text2>
 Akin to tag-search, this query searches for *partial matches of text* in tags.
 The above search includes all occurrences of <text1> without <text2>.
 '''),
 (kw.count+' untagged tagged selection info search '+pkw(),'''
 (**-?**|**-count**) [<tag-substring-to-search-for>]
 Display tag occurrences (of current selection) sorted by amount.
 '''),
 (kw.less+' '+kw.over+' '+kw.equal+' untagged tagged selection search '+pkw(),'''
 (**->**|**-tags>**)
 (**-<**|**-tags<**)
 (**-=**|**-tags=**)
 Select items with specific tag count (from current selection).
 '''),
 (kw.dir+' directory directories selection info show display '+pkw(),'''
 (**-dir**|**-directory-distribution**)
 Display file distribution (of current selection) by location and amount.
 '''),
 (kw.c+' '+kw.ch+' '+kw.ct+' copy hash '+pkw(),'''
 (**-c**|**-copy-filepath**|**-clipboard**) [<index/slice>]
 (**-ch**|**-copy-hash**) [<index/slice>]
 (**-ct**|**-copy-tags**) [<index/slice>]
 Clipboard copy. Works with multiple items eg: "-c :3 3 4:".
 '''),
 (kw.wordnetOn+' '+kw.wordnetOff+' '+kw.wordnetDl+' nltk '+pkw(),'''
 To use *word-substitution* (wordnet) in tag search:
    1. Download the dictionary resources by typing: "**-wordnet-download**"
    2. Set "**use_wordnet = True**" in the ini/config file.
       or use wordnet flag as *parameter* as described below:

 (**-w+**|**-wordnet+**|**-w**|**-wordnet**)
 Enables wordnet on init (parameter overrides ini setting) or in script.

 (**-w-**|**-wordnet-**)
 Disables wordnet on init (parameter overrides ini setting) or in script.
 '''),
 (kw.cls+' screen '+pkw(),'''
 (**-cls**|**-clear**)
 Clears the console screen.
 '''),
 (kw.exit+' bye end '+pkw(),'''
 (**-exit**|**-quit**|**-q**)
 Terminates Inferact - useful in batch processsing.
 '''),
 (kw.inverse+' selection inversion inverse '+pkw(),'''
 (**-inv**|**-inverse-selection**)
 Inverses the current metadata selection.
 '''),
 (kw.sort+' selection sorting order '+pkw(),'''
 (**-sort**)
 Sorts the current metadata selection.
 '''),
 (kw.reverse+' selection sorting order '+pkw(),'''
 (**-rev**|**-reverse**)
 Reverses the order of the selection.
 '''),
 (kw.shuffle+' selection inversion inverse random order '+pkw(),'''
 (**-shuffle**|**-unsort**)
 Shuffles the current metadata selection.
 '''),
 (kw.cfg+' configuration setup options '+pkw(),'''
 (**-cfg**|**-ini**)
 Opens the configuration file.
 '''),
 (kw.color+' colors colours tint red green blue cyan yellow magenta white '+pkw(),'''
 **-color** <color-name>
 Changes the primary color (red, green, blue, cyan, yellow, magenta, white).
 '''),
 (kw.chdir+' dir directory directories '+pkw(),'''
 (**-cd**|**-chdir**) [<new/root/directory>]
 Changes the root directory. For info on current directory,
 use the command only, without the directory part.
 '''),
 (kw.detach+' file files '+pkw(),'''
 **-detach**
 Clears the URL of the selected files.
 '''),
 (kw.rehash+' file files hash '+pkw(),'''
 **-rehash** [(hashed|skipped)]
 Re-calculates the hash value for the selected files.
 Optionally selects already hashed or skipped items (default is all).
 '''),
 (PARA('group groups variant variants item items file files'),'''
--------------------------------------------------------------------------------
# *Groups & Variants*
--------------------------------------------------------------------------------
 '''),
 (kw.group+' gather '+pkw(),'''
 (**-g**|**-group**) [<filename>]
 Adds selected files to a variant group.
 '''),
 (kw.ungroup+' gather '+pkw(),'''
 (**-g-**|**-group-**) <filename>
 Removes file from it's variant group.
 '''),
 (kw.variants+' gathered grouped '+pkw(),'''
 (**-v**|**-variant**)
 Searches for file variants in the current selection.
 '''),
 (kw.variantsAdd+' add gathered grouped '+pkw(),'''
 (**-v+**|**-variant+**)
 Searches for file variants and *adds* them to the current selection.
 '''),
 (kw.variantsSub+' sub substract gathered grouped '+pkw(),'''
 (**-v-**|**-variant-**)
 Searches for file variants and *subtracts* them from the current selection.
 '''),
 (PARA('similar similarity search research'),'''
--------------------------------------------------------------------------------
# *Similarity search*
--------------------------------------------------------------------------------
 '''),
 (kw.similar+' '+pkw(),'''
 (**-sim**|**-similar**) [<similarity%> [reduce-not]]
 Searches for similar files in the database using mixed methods (recommended).
 '''),
 (kw.pSimilar+' '+pkw(),'''
 (**-psim**|**-psimilar**) [<similarity%> [reduce-not]]
 Searches *perceptaully* for similar files (images) in the database.
 '''),
 (kw.similarFuz+' '+pkw(),'''
 (**-simf**|**-similarf**) [<similarity%> [reduce-not]]
 Searches for similar items in the database (method 2).
 '''),
 (kw.pSimilarFuz+' '+pkw(),'''
 (**-psimf**|**-psimilarf**) [<similarity%> [reduce-not]]
 Searches *perceptually* for similar items (images) in the database (method 2).
 '''),
 ('''
 *All* tags in selection are used if *reduce-not* is specified (CPU consuming).
 '''),
 (PARA('script scripting multiple multitask multitasking automation execution'),'''
--------------------------------------------------------------------------------
# *Scripting*
--------------------------------------------------------------------------------
 '''),
 (kw.script+' script scripting file '+pkw(),'''
 **-script** <script-filename>
 By default, files wit the extension *.nfr* (this can be changed in the ini
 settings, under *auto_script_extension*) are executed either with or without
 the *-script* command. Any other file must have this command in order to be
 executed as script. Script commands are delimited by semicolons (*;*) or
 new-lines.
 '''),
 (kw.runClipboard+' clipboard script scripting '+pkw(),'''
 (**-xc**|**-execute-clipboard**|**-run-clipboard**)
 Commands that are manually typed can also be executed directly from the
 system's clipboard.
 ''')
]

text = ''
keywords = []
for i,e in enumerate(help):
    if not isinstance(e, str): # it's a tuple:
        #e[0] = e[0].split()
        for word in e[0].split():
            if len(word)>1 and word.startswith('-'):
                help[i] = (help[i][0]+' '+word[1:], help[i][1])
                #keywords.append(word[1:])
        keywords += help[i][0].split()
        #e[0] = ' '.join(e[0])
        e = e[1]
    text += e
keywords = list(set(keywords))
keywords.sort()
keywords = tuple(keywords)
help = tuple(help)

def get(word):
    ret = ''
    for e in help:
        if not isinstance(e, str) and word in e[0].split():
            ret += e[1]
    ret = ret.split('\n')
    for i,ln in enumerate(ret):
        if ln.strip() == '':
            ret[i] = None
        else:
            break # text
    for i,ln in enumerate(ret[::-1]):
        if ln.strip() == '':
            ret[-1-i] = None
        else:
            break # text
    #return ret.strip()
    return '\n'.join(filter(None,ret))