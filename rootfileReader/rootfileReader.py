#dirname = 'nanoAODcrab/SingleMuon/jun10/180610_172237/'
#outname = ''

import os, sys
from ROOT import TFile, TH1F, TTree, TChain

class pcol:
    end = '\033[0m'
    blue = '\033[1;94m'
    cyan = '\033[1;96m'
    green = '\033[1;92m'
    purple = '\033[1;95m'
    orange = '\033[1;93m'
    red = '\033[1;91m'
    white = '\033[1;97m'

def printerror(message):
  print '\033[1;41mERROR\033[0m \033[91m' + message + '\033[0m'

def printwarning(message):
  print '\033[1;43mWARNING\033[0m \033[93m' + message + '\033[0m'

def GetEntries(trees, treeName = 'Events'):
  while '  ' in trees: trees = trees.replace('  ', ' ')
  treelist = []
  if ' ' in trees: treelist = trees.split(' ')
  else: treelist.append(trees)
  c = TChain(treeName, treeName)
  for t in treelist: c.Add(t)
  return c.GetEntries()

def hadd(rootfiles, outname, index, outdir = './', pretend = False, force = False, verbose = 1):
  out = outdir + 'Tree_' + outname + '_' + str(index) + '.root'
  inp = ''
  for f in rootfiles: inp += f + ' '
  if(len(rootfiles) == 1): 
    command = 'cp ' + inp + ' ' + outdir + out
    if verbose >= 1: printwarning('Only one file! Using cp instead of hadd...')
  else: 
    command = 'python haddnano.py ' + out + ' ' + inp # -ff -O
    if verbose >= 1: print ' >> ' + pcol.green + 'Hadding ', len(rootfiles), ' files into ' + pcol.red , out + pcol.end
  #print '    ' + pcol.red + command + pcol.end
  if os.path.isfile(out):
    if verbose >= 1: printwarning('File already exists!!: ' + out)
    if verbose >= 1: print pcol.red + 'Skipping...' + pcol.end
    iEntries = GetEntries(inp)
    oEntries = GetEntries(out)
    if iEntries != oEntries:
       printerror('NOT SAME NUMBER OF ENTRIES IN INPUT (%i) AND OUTPUT (%i)'%(iEntries, oEntries))
    else: print pcol.green + 'GOOD!!!' + pcol.end
    return
  if not pretend: os.system(command)
  iEntries = GetEntries(inp)
  oEntries = GetEntries(out)
  if iEntries != oEntries:
    printerror('NOT SAME NUMBER OF ENTRIES IN INPUT (%i) AND OUTPUT (%i)'%(iEntries, oEntries))

def haddtrees(dirname, outname, outdir = './', maxsize = 5000, pretend = False, verbose = 1):
  if not outdir[-1] == '/': outdir += '/'
  index = 0
  rootfiles = []
  size = 0
  if outname[-5:] == '.root': outname = outname[:-5]
  if verbose >= 1: print 'Looking into: ', dirname
  for path, subdirs, files in os.walk(dirname):
    for name in files:
      if name[-5:] != '.root': continue 
      fname = path + '/' + name
      command = "ls -lk " + fname + " $totfile | awk '{print $5}'"
      out = float(os.popen(command).read())/1000000
      size += out
      if size < maxsize: 
        if verbose >= 1: print 'Adding ' + pcol.orange + name + pcol.end + ' (' + pcol.cyan + '%1.0f MB' %(out) + pcol.end + '). ' + pcol.white + 'Total: %1.0f MB' %(size) + pcol.end
        rootfiles.append(fname)
      else:
        hadd(rootfiles, outname, index, outdir, pretend)
        index += 1
        rootfiles = []
        size = out
        if verbose >= 1: print 'Adding ' + pcol.orange + name + pcol.end + ' (' + pcol.cyan + '%1.0f MB' %(out) + pcol.end + '). ' + pcol.white + 'Total: %1.0f MB' %(size) + pcol.end
        rootfiles.append(fname)
  if   len(rootfiles) == 0:
    printerror('Files not found!')
  else:
    hadd(rootfiles, outname, index, outdir, pretend)
    index += 1
  #PrintCount(outname)

def GetFiles(outname, outname2 = ''):
  if outname2 == '':
    if '/' in outname:
      n = outname.rfind('/')
      dirname = outname[:n+1]
      outname = outname[n+1:]
    else: dirname = './'
  else:
    dirname = outname
    outname = outname2
    if dirname[-1] != '/': dirname += '/'
  files = []
  snum = ''
  nlenout = len(outname)
  for f in os.listdir(dirname): 
    fname = ''
    snum = 'x'
    if f[-5:] != '.root': continue
    else: f = f[:-5]
    if   f.startswith(outname):           
      snum = f[nlenout+1:]
      fname = outname
    elif f.startswith('Tree_' + outname): 
      snum = f[5+nlenout+1:]
      fname = 'Tree_' + outname
    if snum.isdigit(): 
      fname = fname + '_' + snum + '.root'
      if dirname != './': fname = dirname + fname
      files.append(fname)   
  return files

def GetOnlyCount(files, sCount = 'Count'):
  if isinstance(files, list):
    sumc = 0;
    tfiles = []
    for f in files:
      c = GetOnlyCount(f)
      sumc += c
    return sumc
  else:
    count = 0; 
    #print '...reading file "%s"'%files
    f = TFile.Open(files)
    hCount = TH1F()
    f.GetObject(sCount, hCount)
    if isinstance(hCount, TH1F): 
      count = hCount.GetBinContent(1) 
    f.Close()
    return count

def GetCount(files, sCount = 'Count', sSumOfWeights = 'SumWeights', treename = 'Events'):
  if isinstance(files, list):
    suma = 0; sumb = 0; sumc = 0;
    for f in files:
      a, b, c = GetCount(f)
      suma += a; sumb += b; sumc = c
    return [suma, sumb, sumc]
  else:
    count = 0; sow = 0; entries = 0
    f = TFile.Open(files)
    hCount      = f.Get(sCount)
    hSumWeights = f.Get(sSumOfWeights)
    tree        = f.Get(treename)
    if isinstance(hCount,      TH1F): count   = hCount.GetBinContent(1) 
    if isinstance(hSumWeights, TH1F): sow     = hSumWeights.GetBinContent(1)
    if isinstance(tree,       TTree): entries = tree.GetEntries()
    f.Close()
    return [entries, count, sow]

def PrintCount(outname, outname2 = ''):
  files = GetFiles(outname, outname2)
  if outname2 != '' and outname[-1] != '/': outname += '/'
  print pcol.purple + ' ## Serching for samples with name: ' + pcol.red + outname2 + pcol.purple + "..." + pcol.end 
  if len(files) == 0:
    printerror('Files not found...')
  else:
    print ' >> ' + pcol.blue + 'Total number of files:      ' + pcol.green, len(files),  pcol.end
    entries, count, sumweights = GetCount(files)
    print ' >> ' + pcol.blue + 'Total processed (count):    ' + pcol.green, count,      pcol.end
    print ' >> ' + pcol.blue + 'Sum of gen weights:         ' + pcol.green, sumweights, pcol.end
    print ' >> ' + pcol.blue + 'Total entries (after skim): ' + pcol.green, entries,    pcol.end

def GetSampleListInDir(dirname):
  listofsamples = []
  for s in os.listdir(dirname):
    if not s[-5:] == '.root': continue
    if s.startswith('Tree_'): s = s[5:]
    s = s[:-5]
    digit = ''
    while s[-1].isdigit(): 
      digit = digit + s[-1]
      s = s[:-1]
    if(len(digit)) > 0 and s[-1] == '_': s = s[:-1]
    else: s += digit
    if not s in listofsamples: listofsamples.append(s)
  return sorted(listofsamples)

def CraftSampleName(name):
  # Deal with 'ext' in the end
  if   'ext' in name[-3:]: name = name[:-3] + '_' + name[-3:]
  elif 'ext' in name[-4:]: name = name[:-4] + '_' + name[-4:]
  # Rename bits...
  name = name.replace('madgraphMLM', 'MLM')
  name = name.replace('ST_tW_top', 'tW')
  name = name.replace('ST_tW_antitop', 'tbarW')
  name = name.replace('NoFullyHadronicDecays', 'noFullHad')
  # Delete bits...
  deleteWords = ['13TeV', 'powheg', 'Powheg', 'pythia8']
  s = name.replace('-', '_').split('_')
  a = ''
  for bit in s:
    if bit in deleteWords: continue    
    else: a += '_' + bit
  if a.startswith('_'): a = a[1:]
  if a.endswith('_')  : a = a[:-1]
  while '__' in a: a = a.replace('__', '_')
  return a

def haddProduction(dirname, prodname, verbose = 1):
  dirnames = []
  samplenames = []
  n = len(prodname)
  for path, subdirs, files in os.walk(dirname):
    for s in subdirs:
      if not s.startswith(prodname+'_'): continue
      else:
        treeName = s[n+1:]
        dirName  = path + '/' + s
        sampleName = CraftSampleName(treeName)
        dirnames.append(dirName)
        samplenames.append(sampleName)
        #print 'Looking for ' + treeName + ' in ' + dirName + '...'
        if verbose >= 1: print ' >> Found sample: ' + pcol.red + treeName + pcol.white + ' (' + pcol.cyan + sampleName + pcol.white + ')' + pcol.end
        #print '    In: ' + pcol.purple + dirName + pcol.end
  return [dirnames, samplenames]

def FixStringLength(s, n = 45):
  ''' Fix the length of a string... for nice output '''
  while len(s) < n: s += ' '
  while len(s) > n: s = s[:-1]
  return s

def GetDic(p, f):
    d = {}
    n = len(f)
    if isinstance(p,str):
        p = [p]*n
    for i in range(n): d[f[i]] = p[i]
    return d

def SearchFiles(path, prodname = '', fname = ''):
    ''' Search for files in a production or in a dir (for merged files...) 
        returns a dictionary with paths and filenames
        or a [path, fname] in case of espeficied fname '''
    if prodname != '':
        paths, files = haddProduction(path, prodname, verbose = 0)
        d = GetDic(paths,files)
    else:
        f = GetSampleListInDir(path)
        d = GetDic(path, f)
    if fname != '':
        if not fname in d.keys():
            print 'ERROR: not found sample %s in %s' %(fname, path)
        else: return [d[fname], fname]
    else: return d

def GetAllTrees(dirname):
  filelist = []
  for path, subdirs, files in os.walk(dirname):
    for name in files:
      if not name.endswith('.root'): continue 
      fname = '%s/%s'%(path,name)
      filelist.append(fname)
  return filelist
