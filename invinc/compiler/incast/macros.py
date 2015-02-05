"""Macro processors for expanding one-line operations to several
lines of code.
"""


__all__ = [
    'IncMacroProcessor',
]


from .nodes import Str
from .structconv import parse_structast, astargs
from .helpers import tuplify, sn
from .nodeconv import IncLangImporter


class IncMacroProcessor(IncLangImporter):
    
    """Expand macro operations."""
    
    def pc(self, source, *, mode=None, **kargs):
        """Helper, allows macros to be defined in terms of other macros."""
        tree = parse_structast(source, mode='code', **kargs)
        return self.run(tree)
    
    # Set macros.
    
    def handle_ms_nsadd(self, f, target, elem):
        return self.pc('''
            if ELEM not in TARGET:
                TARGET.add(ELEM)
            ''', subst={'TARGET': target, 'ELEM': elem})
    
    def handle_ms_nsremove(self, f, target, elem):
        return self.pc('''
            if ELEM in TARGET:
                TARGET.remove(ELEM)
            ''', subst={'TARGET': target, 'ELEM': elem})
    
    def handle_ms_rcadd(self, f, target, elem):
        return self.pc('''
            if ELEM not in TARGET:
                TARGET.add(ELEM)
            else:
                TARGET.incref(ELEM)
            ''', subst={'TARGET': target, 'ELEM': elem})
    
    def handle_ms_rcremove(self, f, target, elem):
        return self.pc('''
            if TARGET.getref(ELEM) == 1:
                TARGET.remove(ELEM)
            else:
                TARGET.decref(ELEM)
            ''', subst={'TARGET': target, 'ELEM': elem})
    
    # Map macros.
    
    def handle_ms_nsassignkey(self, f, target, key, value):
        return self.pc('''
            TARGET.nsdelkey(KEY)
            TARGET.assignkey(KEY, VALUE)
            ''', subst={'TARGET': target, 'KEY': key, 'VALUE': value})
    
    def handle_ms_nsdelkey(self, f, target, key):
        return self.pc('''
            if KEY in TARGET:
                TARGET.delkey(KEY)
            ''', subst={'TARGET': target, 'KEY': key})
    
    def handle_ms_imgadd(self, f, target, key, elem):
        return self.pc('''
            if KEY not in TARGET:
                TARGET.assignkey(KEY, set())
            TARGET[KEY].add(ELEM)
            ''', subst={'TARGET': target, 'KEY': key, 'ELEM': elem})
    
    def handle_ms_imgremove(self, f, target, key, elem):
        return self.pc('''
            TARGET[KEY].remove(ELEM)
            if TARGET[KEY].isempty():
                TARGET.delkey(KEY)
            ''', subst={'TARGET': target, 'KEY': key, 'ELEM': elem})
    
    def handle_ms_nsimgadd(self, f, target, key, elem):
        return self.pc('''
            if KEY not in TARGET:
                TARGET.assignkey(KEY, set())
            TARGET[KEY].nsadd(ELEM)
            ''', subst={'TARGET': target, 'KEY': key, 'ELEM': elem})
    
    def handle_ms_nsimgremove(self, f, target, key, elem):
        return self.pc('''
            if KEY in TARGET:
                if ELEM in TARGET[KEY]:
                    TARGET[KEY].remove(ELEM)
                    if TARGET[KEY].isempty():
                        TARGET.delkey(KEY)
            ''', subst={'TARGET': target, 'KEY': key, 'ELEM': elem})
    
    def handle_ms_rcimgadd(self, f, target, key, elem):
        return self.pc('''
            if KEY not in TARGET:
                TARGET.assignkey(KEY, RCSet())
            TARGET[KEY].rcadd(ELEM)
            ''', subst={'TARGET': target, 'KEY': key, 'ELEM': elem})
    
    def handle_ms_rcimgremove(self, f, target, key, elem):
        return self.pc('''
            TARGET[KEY].rcremove(ELEM)
            if TARGET[KEY].isempty():
                TARGET.delkey(KEY)
            ''', subst={'TARGET': target, 'KEY': key, 'ELEM': elem})
    
    # Setmap macros.
    
    @astargs
    def handle_ms_smassignkey(self, f, target, maskstr:'Str', key, elem,
                              prefix:'Str'):
        from invinc.compiler.set import Mask
        mask = Mask(maskstr)
        assert mask.is_keymask
        # vars for each bound component ((len(mask) - 1) many).
        vars = [prefix + str(i) for i in range(1, len(mask))]
        return self.pc('''
            S_VARS = KEY
            TARGET.add(PARTS)
            ''', subst={'S_VARS': tuplify(vars, lval=True),
                        'KEY': key,
                        'TARGET': target,
                        'PARTS': tuplify(vars + [elem])})
    
    @astargs
    def handle_ms_smdelkey(self, f, target, maskstr:'Str', key,
                           prefix:'Str'):
        from invinc.compiler.set import Mask
        mask = Mask(maskstr)
        assert mask.is_keymask
        # vars for each bound component ((len(mask) - 1) many).
        vars = [prefix + str(i) for i in range(1, len(mask))]
        # var for element component
        evar = prefix + 'elem'
        return self.pc('''
            S_VARS = KEY
            S_EVAR = TARGET.smlookup(MASK, KEY)
            TARGET.remove(PARTS)
            ''', subst={'S_VARS': tuplify(vars, lval=True),
                        'KEY': key,
                        'S_EVAR': evar,
                        'MASK': Str(maskstr),
                        'TARGET': target,
                        'PARTS': tuplify(vars + [evar])})
    
    @astargs
    def handle_ms_smnsassignkey(self, f, target, maskstr:'Str', key, elem,
                                prefix:'Str'):
        from invinc.compiler.set import Mask
        mask = Mask(maskstr)
        assert mask.is_keymask
        # vars for each bound component ((len(mask) - 1) many).
        vars = [prefix + str(i) for i in range(1, len(mask))]
        # var for element component
        evar = prefix + 'elem'
        return self.pc('''
            S_VARS = KEY
            if not setmatch(TARGET, MASK, KEY).isempty():
                S_EVAR = TARGET.smlookup(MASK, KEY)
                TARGET.remove(PARTS_OLD)
            TARGET.add(PARTS_NEW)
            ''', subst={'S_VARS': tuplify(vars, lval=True),
                        'KEY': key,
                        'TARGET': target,
                        'MASK': Str(maskstr),
                        'S_EVAR': evar,
                        'PARTS_OLD': tuplify(vars + [evar]),
                        'PARTS_NEW': tuplify(vars + [elem])})
    
    @astargs
    def handle_ms_smnsdelkey(self, f, target, maskstr:'Str', key,
                             prefix:'Str'):
        from invinc.compiler.set import Mask
        mask = Mask(maskstr)
        assert mask.is_keymask
        # vars for each bound component ((len(mask) - 1) many).
        vars = [prefix + str(i) for i in range(1, len(mask))]
        # var for element component
        evar = prefix + 'elem'
        return self.pc('''
            if not setmatch(TARGET, MASK, KEY).isempty():
                S_VARS = KEY
                S_EVAR = TARGET.smlookup(MASK, KEY)
                TARGET.remove(PARTS)
            ''', subst={'TARGET': target,
                        'MASK': Str(maskstr),
                        'KEY': key,
                        'S_VARS': tuplify(vars, lval=True),
                        'S_EVAR': evar,
                        'PARTS': tuplify(vars + [evar])})
    
    @astargs
    def handle_ms_smreassignkey(self, f, target, maskstr:'Str', key, elem,
                                prefix:'Str'):
        from invinc.compiler.set import Mask
        mask = Mask(maskstr)
        assert mask.is_keymask
        vars = [prefix + str(i) for i in range(1, len(mask))]
        evar = prefix + 'elem'
        return self.pc('''
            S_VARS = KEY
            S_EVAR = TARGET.smlookup(MASK, KEY)
            TARGET.remove(OLD_PARTS)
            TARGET.add(NEW_PARTS)
            ''', subst={'S_VARS': tuplify(vars, lval=True),
                        'KEY': key,
                        'S_EVAR': sn(evar),
                        'TARGET': target,
                        'MASK': Str(maskstr),
                        'OLD_PARTS': tuplify(vars + [evar]),
                        'NEW_PARTS': tuplify(vars + [elem])})
