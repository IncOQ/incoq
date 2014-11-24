###############################################################################
# test_rbac_helper.py                                                         #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Unit tests for the rbac_helper module."""


import unittest

from .rbac_helper import *


class Tester(unittest.TestCase):
    
    def test_opnames(self):
        # Actually, if this fails, the global code in rbac_helper
        # will probably fail first anyway, preventing this unittest
        # from running.
        for n in corerbac_op_names:
            self.assertTrue(n in CoreRBAC.__dict__)
    
    def test_Logger(self):
        rbac = LoggingCoreRBAC()
        rbac.log_AddUser('u1')
        rbac.log_AddRole('r1')
        rbac.AssignUser('u1', 'r1')
        
        exp_log = [('AddUser', 'u1'), ('AddRole', 'r1')]
        
        self.assertEqual(rbac.log, exp_log)
    
    def test_Emitter(self):
        rbac = EmittingCoreRBAC()
        
        self.assertTrue(rbac.emit_AddUser())
        self.assertTrue(rbac.emit_DeleteUser())
        self.assertFalse(rbac.emit_DeleteUser())
        self.assertTrue(rbac.emit_AddUser())
        
        exp_log = [('AddUser', 'u0'), ('DeleteUser', 'u0'), ('AddUser', 'u1')]
        
        self.assertEqual(rbac.log, exp_log)
    
    def test_DemandEmitter(self):
        rbac = DemandEmittingCoreRBAC(1)
        
        # Caution, using non-emit_* variety won't automatically
        # increment the internal fresh-names counters.
        
        rbac.AddUser('u0'),
        rbac.AddRole('r0'),
        rbac.AddOperation('op0'),
        rbac.AddObject('obj0'),
        rbac.GrantPermission('op0', 'obj0', 'r0'),
        rbac.AssignUser('u0', 'r0'),
        rbac.CreateSession('u0', 's0', {'r0'}),
        next(rbac.n_sessions)
        
        # None of these can be done without deleting the single
        # queryable session.
        self.assertFalse(rbac.emit_DeleteUser())
        self.assertFalse(rbac.emit_DeleteRole())
        self.assertFalse(rbac.emit_DeassignUser())
        self.assertFalse(rbac.emit_DeleteSession())
        
        # Ensure CheckAccess uses the queryable session (probabilistic).
        for _ in range(100):
            rbac.emit_CreateSession()
        rbac.emit_CheckAccess()
        self.assertEqual(rbac.log[-1], ('CheckAccess', 's0', 'op0', 'obj0'))


if __name__ == '__main__':
    unittest.main()
