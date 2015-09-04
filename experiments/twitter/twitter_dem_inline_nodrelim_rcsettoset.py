# Manually modified version of twitter_dem_inline_nodrelim.py
# that replaces RCSet() with Set() declarations when rc operations
# aren't needed.

from incoq.runtime import *
# Comp1 := {(celeb, group, user_email) : (celeb, group) in _U_Comp1, (celeb, celeb_followers) in _F_followers, (celeb_followers, user) in _M, (group, user) in _M, (user, user_loc) in _F_loc, (user_loc == 'NYC'), (user, user_email) in _F_email}
# Comp1_Tceleb := {celeb : (celeb, group) in _U_Comp1}
# Comp1_Tgroup := {group : (celeb, group) in _U_Comp1}
# Comp1_d_F_followers := {(celeb, celeb_followers) : celeb in Comp1_Tceleb, (celeb, celeb_followers) in _F_followers}
# Comp1_Tceleb_followers := {celeb_followers : (celeb, celeb_followers) in Comp1_d_F_followers}
# Comp1_d_M1 := {(celeb_followers, user) : celeb_followers in Comp1_Tceleb_followers, (celeb_followers, user) in _M}
# Comp1_Tuser1 := {user : (celeb_followers, user) in Comp1_d_M1}
# Comp1_d_M2 := {(group, user) : group in Comp1_Tgroup, (group, user) in _M}
# Comp1_Tuser2 := {user : (group, user) in Comp1_d_M2}
# Comp1_d_F_loc := {(user, user_loc) : user in Comp1_Tuser1, user in Comp1_Tuser2, (user, user_loc) in _F_loc}
# Comp1_d_F_email := {(user, user_email) : user in Comp1_Tuser1, user in Comp1_Tuser2, (user, user_email) in _F_email}
_m_Comp1_bbu = Map()
_m_Comp1_d_M1_in = Map()
_m__U_Comp1_in = Map()
_m_Comp1_d_F_followers_in = Map()
_m__U_Comp1_out = Map()
Comp1_d_F_email = Set()
Comp1_d_F_loc = Set()
Comp1_Tuser2 = RCSet()
Comp1_d_M2 = Set()
Comp1_Tuser1 = RCSet()
Comp1_d_M1 = Set()
Comp1_Tceleb_followers = RCSet()
Comp1_d_F_followers = Set()
Comp1_Tgroup = RCSet()
Comp1_Tceleb = RCSet()
Comp1 = Set()
_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(celeb, group):
    # Cost: O((v29_group + v23_celeb_followers + v3_celeb_followers))
    "{(celeb, group, user_email) : (celeb, group) in _U_Comp1, (celeb, celeb_followers) in _F_followers, (celeb_followers, user) in _M, (group, user) in _M, (user, user_loc) in _F_loc, (user_loc == 'NYC'), (user, user_email) in _F_email}"
    if ((celeb, group) not in _U_Comp1):
        _U_Comp1.add((celeb, group))
        # Begin maint _m__U_Comp1_in after "_U_Comp1.add((celeb, group))"
        (v51_1, v51_2) = (celeb, group)
        if (v51_2 not in _m__U_Comp1_in):
            _m__U_Comp1_in[v51_2] = set()
        _m__U_Comp1_in[v51_2].add(v51_1)
        # End maint _m__U_Comp1_in after "_U_Comp1.add((celeb, group))"
        # Begin maint _m__U_Comp1_out after "_U_Comp1.add((celeb, group))"
        (v47_1, v47_2) = (celeb, group)
        if (v47_1 not in _m__U_Comp1_out):
            _m__U_Comp1_out[v47_1] = set()
        _m__U_Comp1_out[v47_1].add(v47_2)
        # End maint _m__U_Comp1_out after "_U_Comp1.add((celeb, group))"
        # Begin maint Comp1_Tgroup after "_U_Comp1.add((celeb, group))"
        # Cost: O(v29_group)
        # Iterate {(v15_celeb, v15_group) : (v15_celeb, v15_group) in deltamatch(_U_Comp1, 'bb', _e, 1)}
        (v15_celeb, v15_group) = (celeb, group)
        if (v15_group not in Comp1_Tgroup):
            Comp1_Tgroup.add(v15_group)
            # Begin maint Comp1_d_M2 after "Comp1_Tgroup.add(v15_group)"
            # Cost: O(v29_group)
            # Iterate {(v29_group, v29_user) : v29_group in deltamatch(Comp1_Tgroup, 'b', _e, 1), (v29_group, v29_user) in _M}
            v29_group = v15_group
            if isinstance(v29_group, Set):
                for v29_user in v29_group:
                    Comp1_d_M2.add((v29_group, v29_user))
                    # Begin maint Comp1_Tuser2 after "Comp1_d_M2.add((v29_group, v29_user))"
                    # Cost: O(1)
                    # Iterate {(v33_group, v33_user) : (v33_group, v33_user) in deltamatch(Comp1_d_M2, 'bb', _e, 1)}
                    (v33_group, v33_user) = (v29_group, v29_user)
                    if (v33_user not in Comp1_Tuser2):
                        Comp1_Tuser2.add(v33_user)
                        # Begin maint Comp1_d_F_email after "Comp1_Tuser2.add(v33_user)"
                        # Cost: O(1)
                        # Iterate {(v43_user, v43_user_email) : v43_user in Comp1_Tuser1, v43_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v43_user, v43_user_email) in _F_email}
                        v43_user = v33_user
                        if (v43_user in Comp1_Tuser1):
                            if hasattr(v43_user, 'email'):
                                v43_user_email = v43_user.email
                                Comp1_d_F_email.add((v43_user, v43_user_email))
                        # End maint Comp1_d_F_email after "Comp1_Tuser2.add(v33_user)"
                        # Begin maint Comp1_d_F_loc after "Comp1_Tuser2.add(v33_user)"
                        # Cost: O(1)
                        # Iterate {(v37_user, v37_user_loc) : v37_user in Comp1_Tuser1, v37_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v37_user, v37_user_loc) in _F_loc}
                        v37_user = v33_user
                        if (v37_user in Comp1_Tuser1):
                            if hasattr(v37_user, 'loc'):
                                v37_user_loc = v37_user.loc
                                Comp1_d_F_loc.add((v37_user, v37_user_loc))
                        # End maint Comp1_d_F_loc after "Comp1_Tuser2.add(v33_user)"
                    else:
                        Comp1_Tuser2.incref(v33_user)
                    # End maint Comp1_Tuser2 after "Comp1_d_M2.add((v29_group, v29_user))"
            # End maint Comp1_d_M2 after "Comp1_Tgroup.add(v15_group)"
        else:
            Comp1_Tgroup.incref(v15_group)
        # End maint Comp1_Tgroup after "_U_Comp1.add((celeb, group))"
        # Begin maint Comp1_Tceleb after "_U_Comp1.add((celeb, group))"
        # Cost: O(v23_celeb_followers)
        # Iterate {(v13_celeb, v13_group) : (v13_celeb, v13_group) in deltamatch(_U_Comp1, 'bb', _e, 1)}
        (v13_celeb, v13_group) = (celeb, group)
        if (v13_celeb not in Comp1_Tceleb):
            Comp1_Tceleb.add(v13_celeb)
            # Begin maint Comp1_d_F_followers after "Comp1_Tceleb.add(v13_celeb)"
            # Cost: O(v23_celeb_followers)
            # Iterate {(v17_celeb, v17_celeb_followers) : v17_celeb in deltamatch(Comp1_Tceleb, 'b', _e, 1), (v17_celeb, v17_celeb_followers) in _F_followers}
            v17_celeb = v13_celeb
            if hasattr(v17_celeb, 'followers'):
                v17_celeb_followers = v17_celeb.followers
                Comp1_d_F_followers.add((v17_celeb, v17_celeb_followers))
                # Begin maint _m_Comp1_d_F_followers_in after "Comp1_d_F_followers.add((v17_celeb, v17_celeb_followers))"
                (v49_1, v49_2) = (v17_celeb, v17_celeb_followers)
                if (v49_2 not in _m_Comp1_d_F_followers_in):
                    _m_Comp1_d_F_followers_in[v49_2] = set()
                _m_Comp1_d_F_followers_in[v49_2].add(v49_1)
                # End maint _m_Comp1_d_F_followers_in after "Comp1_d_F_followers.add((v17_celeb, v17_celeb_followers))"
                # Begin maint Comp1_Tceleb_followers after "Comp1_d_F_followers.add((v17_celeb, v17_celeb_followers))"
                # Cost: O(v23_celeb_followers)
                # Iterate {(v21_celeb, v21_celeb_followers) : (v21_celeb, v21_celeb_followers) in deltamatch(Comp1_d_F_followers, 'bb', _e, 1)}
                (v21_celeb, v21_celeb_followers) = (v17_celeb, v17_celeb_followers)
                if (v21_celeb_followers not in Comp1_Tceleb_followers):
                    Comp1_Tceleb_followers.add(v21_celeb_followers)
                    # Begin maint Comp1_d_M1 after "Comp1_Tceleb_followers.add(v21_celeb_followers)"
                    # Cost: O(v23_celeb_followers)
                    # Iterate {(v23_celeb_followers, v23_user) : v23_celeb_followers in deltamatch(Comp1_Tceleb_followers, 'b', _e, 1), (v23_celeb_followers, v23_user) in _M}
                    v23_celeb_followers = v21_celeb_followers
                    if isinstance(v23_celeb_followers, Set):
                        for v23_user in v23_celeb_followers:
                            Comp1_d_M1.add((v23_celeb_followers, v23_user))
                            # Begin maint _m_Comp1_d_M1_in after "Comp1_d_M1.add((v23_celeb_followers, v23_user))"
                            (v53_1, v53_2) = (v23_celeb_followers, v23_user)
                            if (v53_2 not in _m_Comp1_d_M1_in):
                                _m_Comp1_d_M1_in[v53_2] = set()
                            _m_Comp1_d_M1_in[v53_2].add(v53_1)
                            # End maint _m_Comp1_d_M1_in after "Comp1_d_M1.add((v23_celeb_followers, v23_user))"
                            # Begin maint Comp1_Tuser1 after "Comp1_d_M1.add((v23_celeb_followers, v23_user))"
                            # Cost: O(1)
                            # Iterate {(v27_celeb_followers, v27_user) : (v27_celeb_followers, v27_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1)}
                            (v27_celeb_followers, v27_user) = (v23_celeb_followers, v23_user)
                            if (v27_user not in Comp1_Tuser1):
                                Comp1_Tuser1.add(v27_user)
                                # Begin maint Comp1_d_F_email after "Comp1_Tuser1.add(v27_user)"
                                # Cost: O(1)
                                # Iterate {(v41_user, v41_user_email) : v41_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v41_user in Comp1_Tuser2, (v41_user, v41_user_email) in _F_email}
                                v41_user = v27_user
                                if (v41_user in Comp1_Tuser2):
                                    if hasattr(v41_user, 'email'):
                                        v41_user_email = v41_user.email
                                        Comp1_d_F_email.add((v41_user, v41_user_email))
                                # End maint Comp1_d_F_email after "Comp1_Tuser1.add(v27_user)"
                                # Begin maint Comp1_d_F_loc after "Comp1_Tuser1.add(v27_user)"
                                # Cost: O(1)
                                # Iterate {(v35_user, v35_user_loc) : v35_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v35_user in Comp1_Tuser2, (v35_user, v35_user_loc) in _F_loc}
                                v35_user = v27_user
                                if (v35_user in Comp1_Tuser2):
                                    if hasattr(v35_user, 'loc'):
                                        v35_user_loc = v35_user.loc
                                        Comp1_d_F_loc.add((v35_user, v35_user_loc))
                                # End maint Comp1_d_F_loc after "Comp1_Tuser1.add(v27_user)"
                            else:
                                Comp1_Tuser1.incref(v27_user)
                            # End maint Comp1_Tuser1 after "Comp1_d_M1.add((v23_celeb_followers, v23_user))"
                    # End maint Comp1_d_M1 after "Comp1_Tceleb_followers.add(v21_celeb_followers)"
                else:
                    Comp1_Tceleb_followers.incref(v21_celeb_followers)
                # End maint Comp1_Tceleb_followers after "Comp1_d_F_followers.add((v17_celeb, v17_celeb_followers))"
            # End maint Comp1_d_F_followers after "Comp1_Tceleb.add(v13_celeb)"
        else:
            Comp1_Tceleb.incref(v13_celeb)
        # End maint Comp1_Tceleb after "_U_Comp1.add((celeb, group))"
        # Begin maint Comp1 after "_U_Comp1.add((celeb, group))"
        # Cost: O(v3_celeb_followers)
        # Iterate {(v3_celeb, v3_group, v3_celeb_followers, v3_user, v3_user_loc, v3_user_email) : (v3_celeb, v3_group) in deltamatch(_U_Comp1, 'bb', _e, 1), (v3_celeb, v3_celeb_followers) in _F_followers, (v3_celeb_followers, v3_user) in _M, (v3_group, v3_user) in _M, (v3_user, v3_user_loc) in _F_loc, (v3_user_loc == 'NYC'), (v3_user, v3_user_email) in _F_email}
        (v3_celeb, v3_group) = (celeb, group)
        if hasattr(v3_celeb, 'followers'):
            v3_celeb_followers = v3_celeb.followers
            if isinstance(v3_celeb_followers, Set):
                for v3_user in v3_celeb_followers:
                    if isinstance(v3_group, Set):
                        if (v3_user in v3_group):
                            if hasattr(v3_user, 'loc'):
                                v3_user_loc = v3_user.loc
                                if (v3_user_loc == 'NYC'):
                                    if hasattr(v3_user, 'email'):
                                        v3_user_email = v3_user.email
                                        Comp1.add((v3_celeb, v3_group, v3_user_email))
                                        # Begin maint _m_Comp1_bbu after "Comp1.add((v3_celeb, v3_group, v3_user_email))"
                                        (v55_1, v55_2, v55_3) = (v3_celeb, v3_group, v3_user_email)
                                        if ((v55_1, v55_2) not in _m_Comp1_bbu):
                                            _m_Comp1_bbu[(v55_1, v55_2)] = set()
                                        _m_Comp1_bbu[(v55_1, v55_2)].add(v55_3)
                                        # End maint _m_Comp1_bbu after "Comp1.add((v3_celeb, v3_group, v3_user_email))"
        # End maint Comp1 after "_U_Comp1.add((celeb, group))"
    else:
        _U_Comp1.incref((celeb, group))

def undemand_Comp1(celeb, group):
    # Cost: O((v4_celeb_followers + v24_celeb_followers + v30_group))
    "{(celeb, group, user_email) : (celeb, group) in _U_Comp1, (celeb, celeb_followers) in _F_followers, (celeb_followers, user) in _M, (group, user) in _M, (user, user_loc) in _F_loc, (user_loc == 'NYC'), (user, user_email) in _F_email}"
    if (_U_Comp1.getref((celeb, group)) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove((celeb, group))"
        # Cost: O(v4_celeb_followers)
        # Iterate {(v4_celeb, v4_group, v4_celeb_followers, v4_user, v4_user_loc, v4_user_email) : (v4_celeb, v4_group) in deltamatch(_U_Comp1, 'bb', _e, 1), (v4_celeb, v4_celeb_followers) in _F_followers, (v4_celeb_followers, v4_user) in _M, (v4_group, v4_user) in _M, (v4_user, v4_user_loc) in _F_loc, (v4_user_loc == 'NYC'), (v4_user, v4_user_email) in _F_email}
        (v4_celeb, v4_group) = (celeb, group)
        if hasattr(v4_celeb, 'followers'):
            v4_celeb_followers = v4_celeb.followers
            if isinstance(v4_celeb_followers, Set):
                for v4_user in v4_celeb_followers:
                    if isinstance(v4_group, Set):
                        if (v4_user in v4_group):
                            if hasattr(v4_user, 'loc'):
                                v4_user_loc = v4_user.loc
                                if (v4_user_loc == 'NYC'):
                                    if hasattr(v4_user, 'email'):
                                        v4_user_email = v4_user.email
                                        # Begin maint _m_Comp1_bbu before "Comp1.remove((v4_celeb, v4_group, v4_user_email))"
                                        (v56_1, v56_2, v56_3) = (v4_celeb, v4_group, v4_user_email)
                                        _m_Comp1_bbu[(v56_1, v56_2)].remove(v56_3)
                                        if (len(_m_Comp1_bbu[(v56_1, v56_2)]) == 0):
                                            del _m_Comp1_bbu[(v56_1, v56_2)]
                                        # End maint _m_Comp1_bbu before "Comp1.remove((v4_celeb, v4_group, v4_user_email))"
                                        Comp1.remove((v4_celeb, v4_group, v4_user_email))
        # End maint Comp1 before "_U_Comp1.remove((celeb, group))"
        # Begin maint Comp1_Tceleb before "_U_Comp1.remove((celeb, group))"
        # Cost: O(v24_celeb_followers)
        # Iterate {(v14_celeb, v14_group) : (v14_celeb, v14_group) in deltamatch(_U_Comp1, 'bb', _e, 1)}
        (v14_celeb, v14_group) = (celeb, group)
        if (Comp1_Tceleb.getref(v14_celeb) == 1):
            # Begin maint Comp1_d_F_followers before "Comp1_Tceleb.remove(v14_celeb)"
            # Cost: O(v24_celeb_followers)
            # Iterate {(v18_celeb, v18_celeb_followers) : v18_celeb in deltamatch(Comp1_Tceleb, 'b', _e, 1), (v18_celeb, v18_celeb_followers) in _F_followers}
            v18_celeb = v14_celeb
            if hasattr(v18_celeb, 'followers'):
                v18_celeb_followers = v18_celeb.followers
                # Begin maint Comp1_Tceleb_followers before "Comp1_d_F_followers.remove((v18_celeb, v18_celeb_followers))"
                # Cost: O(v24_celeb_followers)
                # Iterate {(v22_celeb, v22_celeb_followers) : (v22_celeb, v22_celeb_followers) in deltamatch(Comp1_d_F_followers, 'bb', _e, 1)}
                (v22_celeb, v22_celeb_followers) = (v18_celeb, v18_celeb_followers)
                if (Comp1_Tceleb_followers.getref(v22_celeb_followers) == 1):
                    # Begin maint Comp1_d_M1 before "Comp1_Tceleb_followers.remove(v22_celeb_followers)"
                    # Cost: O(v24_celeb_followers)
                    # Iterate {(v24_celeb_followers, v24_user) : v24_celeb_followers in deltamatch(Comp1_Tceleb_followers, 'b', _e, 1), (v24_celeb_followers, v24_user) in _M}
                    v24_celeb_followers = v22_celeb_followers
                    if isinstance(v24_celeb_followers, Set):
                        for v24_user in v24_celeb_followers:
                            # Begin maint Comp1_Tuser1 before "Comp1_d_M1.remove((v24_celeb_followers, v24_user))"
                            # Cost: O(1)
                            # Iterate {(v28_celeb_followers, v28_user) : (v28_celeb_followers, v28_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1)}
                            (v28_celeb_followers, v28_user) = (v24_celeb_followers, v24_user)
                            if (Comp1_Tuser1.getref(v28_user) == 1):
                                # Begin maint Comp1_d_F_loc before "Comp1_Tuser1.remove(v28_user)"
                                # Cost: O(1)
                                # Iterate {(v36_user, v36_user_loc) : v36_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v36_user in Comp1_Tuser2, (v36_user, v36_user_loc) in _F_loc}
                                v36_user = v28_user
                                if (v36_user in Comp1_Tuser2):
                                    if hasattr(v36_user, 'loc'):
                                        v36_user_loc = v36_user.loc
                                        Comp1_d_F_loc.remove((v36_user, v36_user_loc))
                                # End maint Comp1_d_F_loc before "Comp1_Tuser1.remove(v28_user)"
                                # Begin maint Comp1_d_F_email before "Comp1_Tuser1.remove(v28_user)"
                                # Cost: O(1)
                                # Iterate {(v42_user, v42_user_email) : v42_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v42_user in Comp1_Tuser2, (v42_user, v42_user_email) in _F_email}
                                v42_user = v28_user
                                if (v42_user in Comp1_Tuser2):
                                    if hasattr(v42_user, 'email'):
                                        v42_user_email = v42_user.email
                                        Comp1_d_F_email.remove((v42_user, v42_user_email))
                                # End maint Comp1_d_F_email before "Comp1_Tuser1.remove(v28_user)"
                                Comp1_Tuser1.remove(v28_user)
                            else:
                                Comp1_Tuser1.decref(v28_user)
                            # End maint Comp1_Tuser1 before "Comp1_d_M1.remove((v24_celeb_followers, v24_user))"
                            # Begin maint _m_Comp1_d_M1_in before "Comp1_d_M1.remove((v24_celeb_followers, v24_user))"
                            (v54_1, v54_2) = (v24_celeb_followers, v24_user)
                            _m_Comp1_d_M1_in[v54_2].remove(v54_1)
                            if (len(_m_Comp1_d_M1_in[v54_2]) == 0):
                                del _m_Comp1_d_M1_in[v54_2]
                            # End maint _m_Comp1_d_M1_in before "Comp1_d_M1.remove((v24_celeb_followers, v24_user))"
                            Comp1_d_M1.remove((v24_celeb_followers, v24_user))
                    # End maint Comp1_d_M1 before "Comp1_Tceleb_followers.remove(v22_celeb_followers)"
                    Comp1_Tceleb_followers.remove(v22_celeb_followers)
                else:
                    Comp1_Tceleb_followers.decref(v22_celeb_followers)
                # End maint Comp1_Tceleb_followers before "Comp1_d_F_followers.remove((v18_celeb, v18_celeb_followers))"
                # Begin maint _m_Comp1_d_F_followers_in before "Comp1_d_F_followers.remove((v18_celeb, v18_celeb_followers))"
                (v50_1, v50_2) = (v18_celeb, v18_celeb_followers)
                _m_Comp1_d_F_followers_in[v50_2].remove(v50_1)
                if (len(_m_Comp1_d_F_followers_in[v50_2]) == 0):
                    del _m_Comp1_d_F_followers_in[v50_2]
                # End maint _m_Comp1_d_F_followers_in before "Comp1_d_F_followers.remove((v18_celeb, v18_celeb_followers))"
                Comp1_d_F_followers.remove((v18_celeb, v18_celeb_followers))
            # End maint Comp1_d_F_followers before "Comp1_Tceleb.remove(v14_celeb)"
            Comp1_Tceleb.remove(v14_celeb)
        else:
            Comp1_Tceleb.decref(v14_celeb)
        # End maint Comp1_Tceleb before "_U_Comp1.remove((celeb, group))"
        # Begin maint Comp1_Tgroup before "_U_Comp1.remove((celeb, group))"
        # Cost: O(v30_group)
        # Iterate {(v16_celeb, v16_group) : (v16_celeb, v16_group) in deltamatch(_U_Comp1, 'bb', _e, 1)}
        (v16_celeb, v16_group) = (celeb, group)
        if (Comp1_Tgroup.getref(v16_group) == 1):
            # Begin maint Comp1_d_M2 before "Comp1_Tgroup.remove(v16_group)"
            # Cost: O(v30_group)
            # Iterate {(v30_group, v30_user) : v30_group in deltamatch(Comp1_Tgroup, 'b', _e, 1), (v30_group, v30_user) in _M}
            v30_group = v16_group
            if isinstance(v30_group, Set):
                for v30_user in v30_group:
                    # Begin maint Comp1_Tuser2 before "Comp1_d_M2.remove((v30_group, v30_user))"
                    # Cost: O(1)
                    # Iterate {(v34_group, v34_user) : (v34_group, v34_user) in deltamatch(Comp1_d_M2, 'bb', _e, 1)}
                    (v34_group, v34_user) = (v30_group, v30_user)
                    if (Comp1_Tuser2.getref(v34_user) == 1):
                        # Begin maint Comp1_d_F_loc before "Comp1_Tuser2.remove(v34_user)"
                        # Cost: O(1)
                        # Iterate {(v38_user, v38_user_loc) : v38_user in Comp1_Tuser1, v38_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v38_user, v38_user_loc) in _F_loc}
                        v38_user = v34_user
                        if (v38_user in Comp1_Tuser1):
                            if hasattr(v38_user, 'loc'):
                                v38_user_loc = v38_user.loc
                                Comp1_d_F_loc.remove((v38_user, v38_user_loc))
                        # End maint Comp1_d_F_loc before "Comp1_Tuser2.remove(v34_user)"
                        # Begin maint Comp1_d_F_email before "Comp1_Tuser2.remove(v34_user)"
                        # Cost: O(1)
                        # Iterate {(v44_user, v44_user_email) : v44_user in Comp1_Tuser1, v44_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v44_user, v44_user_email) in _F_email}
                        v44_user = v34_user
                        if (v44_user in Comp1_Tuser1):
                            if hasattr(v44_user, 'email'):
                                v44_user_email = v44_user.email
                                Comp1_d_F_email.remove((v44_user, v44_user_email))
                        # End maint Comp1_d_F_email before "Comp1_Tuser2.remove(v34_user)"
                        Comp1_Tuser2.remove(v34_user)
                    else:
                        Comp1_Tuser2.decref(v34_user)
                    # End maint Comp1_Tuser2 before "Comp1_d_M2.remove((v30_group, v30_user))"
                    Comp1_d_M2.remove((v30_group, v30_user))
            # End maint Comp1_d_M2 before "Comp1_Tgroup.remove(v16_group)"
            Comp1_Tgroup.remove(v16_group)
        else:
            Comp1_Tgroup.decref(v16_group)
        # End maint Comp1_Tgroup before "_U_Comp1.remove((celeb, group))"
        # Begin maint _m__U_Comp1_out before "_U_Comp1.remove((celeb, group))"
        (v48_1, v48_2) = (celeb, group)
        _m__U_Comp1_out[v48_1].remove(v48_2)
        if (len(_m__U_Comp1_out[v48_1]) == 0):
            del _m__U_Comp1_out[v48_1]
        # End maint _m__U_Comp1_out before "_U_Comp1.remove((celeb, group))"
        # Begin maint _m__U_Comp1_in before "_U_Comp1.remove((celeb, group))"
        (v52_1, v52_2) = (celeb, group)
        _m__U_Comp1_in[v52_2].remove(v52_1)
        if (len(_m__U_Comp1_in[v52_2]) == 0):
            del _m__U_Comp1_in[v52_2]
        # End maint _m__U_Comp1_in before "_U_Comp1.remove((celeb, group))"
        _U_Comp1.remove((celeb, group))
    else:
        _U_Comp1.decref((celeb, group))

def query_Comp1(celeb, group):
    # Cost: O((v29_group + v23_celeb_followers + v3_celeb_followers))
    "{(celeb, group, user_email) : (celeb, group) in _U_Comp1, (celeb, celeb_followers) in _F_followers, (celeb_followers, user) in _M, (group, user) in _M, (user, user_loc) in _F_loc, (user_loc == 'NYC'), (user, user_email) in _F_email}"
    if ((celeb, group) not in _UEXT_Comp1):
        _UEXT_Comp1.add((celeb, group))
        demand_Comp1(celeb, group)
    return True

def make_user(email, loc):
    # Cost: O((v23_celeb_followers + (_U_Comp1_out*v5_celeb_followers) + (_U_Comp1_out*Comp1_d_F_followers_in*Comp1_d_M1_in)))
    u = Obj()
    u.followers = Set()
    # Begin maint Comp1_d_F_followers after "_F_followers.add((u, Set()))"
    # Cost: O(v23_celeb_followers)
    # Iterate {(v19_celeb, v19_celeb_followers) : v19_celeb in Comp1_Tceleb, (v19_celeb, v19_celeb_followers) in deltamatch(_F_followers, 'bb', _e, 1)}
    (v19_celeb, v19_celeb_followers) = (u, Set())
    if (v19_celeb in Comp1_Tceleb):
        Comp1_d_F_followers.add((v19_celeb, v19_celeb_followers))
        # Begin maint _m_Comp1_d_F_followers_in after "Comp1_d_F_followers.add((v19_celeb, v19_celeb_followers))"
        (v49_1, v49_2) = (v19_celeb, v19_celeb_followers)
        if (v49_2 not in _m_Comp1_d_F_followers_in):
            _m_Comp1_d_F_followers_in[v49_2] = set()
        _m_Comp1_d_F_followers_in[v49_2].add(v49_1)
        # End maint _m_Comp1_d_F_followers_in after "Comp1_d_F_followers.add((v19_celeb, v19_celeb_followers))"
        # Begin maint Comp1_Tceleb_followers after "Comp1_d_F_followers.add((v19_celeb, v19_celeb_followers))"
        # Cost: O(v23_celeb_followers)
        # Iterate {(v21_celeb, v21_celeb_followers) : (v21_celeb, v21_celeb_followers) in deltamatch(Comp1_d_F_followers, 'bb', _e, 1)}
        (v21_celeb, v21_celeb_followers) = (v19_celeb, v19_celeb_followers)
        if (v21_celeb_followers not in Comp1_Tceleb_followers):
            Comp1_Tceleb_followers.add(v21_celeb_followers)
            # Begin maint Comp1_d_M1 after "Comp1_Tceleb_followers.add(v21_celeb_followers)"
            # Cost: O(v23_celeb_followers)
            # Iterate {(v23_celeb_followers, v23_user) : v23_celeb_followers in deltamatch(Comp1_Tceleb_followers, 'b', _e, 1), (v23_celeb_followers, v23_user) in _M}
            v23_celeb_followers = v21_celeb_followers
            if isinstance(v23_celeb_followers, Set):
                for v23_user in v23_celeb_followers:
                    Comp1_d_M1.add((v23_celeb_followers, v23_user))
                    # Begin maint _m_Comp1_d_M1_in after "Comp1_d_M1.add((v23_celeb_followers, v23_user))"
                    (v53_1, v53_2) = (v23_celeb_followers, v23_user)
                    if (v53_2 not in _m_Comp1_d_M1_in):
                        _m_Comp1_d_M1_in[v53_2] = set()
                    _m_Comp1_d_M1_in[v53_2].add(v53_1)
                    # End maint _m_Comp1_d_M1_in after "Comp1_d_M1.add((v23_celeb_followers, v23_user))"
                    # Begin maint Comp1_Tuser1 after "Comp1_d_M1.add((v23_celeb_followers, v23_user))"
                    # Cost: O(1)
                    # Iterate {(v27_celeb_followers, v27_user) : (v27_celeb_followers, v27_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1)}
                    (v27_celeb_followers, v27_user) = (v23_celeb_followers, v23_user)
                    if (v27_user not in Comp1_Tuser1):
                        Comp1_Tuser1.add(v27_user)
                        # Begin maint Comp1_d_F_email after "Comp1_Tuser1.add(v27_user)"
                        # Cost: O(1)
                        # Iterate {(v41_user, v41_user_email) : v41_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v41_user in Comp1_Tuser2, (v41_user, v41_user_email) in _F_email}
                        v41_user = v27_user
                        if (v41_user in Comp1_Tuser2):
                            if hasattr(v41_user, 'email'):
                                v41_user_email = v41_user.email
                                Comp1_d_F_email.add((v41_user, v41_user_email))
                        # End maint Comp1_d_F_email after "Comp1_Tuser1.add(v27_user)"
                        # Begin maint Comp1_d_F_loc after "Comp1_Tuser1.add(v27_user)"
                        # Cost: O(1)
                        # Iterate {(v35_user, v35_user_loc) : v35_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v35_user in Comp1_Tuser2, (v35_user, v35_user_loc) in _F_loc}
                        v35_user = v27_user
                        if (v35_user in Comp1_Tuser2):
                            if hasattr(v35_user, 'loc'):
                                v35_user_loc = v35_user.loc
                                Comp1_d_F_loc.add((v35_user, v35_user_loc))
                        # End maint Comp1_d_F_loc after "Comp1_Tuser1.add(v27_user)"
                    else:
                        Comp1_Tuser1.incref(v27_user)
                    # End maint Comp1_Tuser1 after "Comp1_d_M1.add((v23_celeb_followers, v23_user))"
            # End maint Comp1_d_M1 after "Comp1_Tceleb_followers.add(v21_celeb_followers)"
        else:
            Comp1_Tceleb_followers.incref(v21_celeb_followers)
        # End maint Comp1_Tceleb_followers after "Comp1_d_F_followers.add((v19_celeb, v19_celeb_followers))"
    # End maint Comp1_d_F_followers after "_F_followers.add((u, Set()))"
    # Begin maint Comp1 after "_F_followers.add((u, Set()))"
    # Cost: O((_U_Comp1_out*v5_celeb_followers))
    # Iterate {(v5_celeb, v5_group, v5_celeb_followers, v5_user, v5_user_loc, v5_user_email) : (v5_celeb, v5_group) in _U_Comp1, (v5_celeb, v5_celeb_followers) in deltamatch(Comp1_d_F_followers, 'bb', _e, 1), (v5_celeb, v5_celeb_followers) in Comp1_d_F_followers, (v5_celeb_followers, v5_user) in _M, (v5_group, v5_user) in _M, (v5_user, v5_user_loc) in _F_loc, (v5_user_loc == 'NYC'), (v5_user, v5_user_email) in _F_email}
    (v5_celeb, v5_celeb_followers) = (u, Set())
    if ((v5_celeb, v5_celeb_followers) in Comp1_d_F_followers):
        for v5_group in (_m__U_Comp1_out[v5_celeb] if (v5_celeb in _m__U_Comp1_out) else set()):
            if isinstance(v5_celeb_followers, Set):
                for v5_user in v5_celeb_followers:
                    if isinstance(v5_group, Set):
                        if (v5_user in v5_group):
                            if hasattr(v5_user, 'loc'):
                                v5_user_loc = v5_user.loc
                                if (v5_user_loc == 'NYC'):
                                    if hasattr(v5_user, 'email'):
                                        v5_user_email = v5_user.email
                                        Comp1.add((v5_celeb, v5_group, v5_user_email))
                                        # Begin maint _m_Comp1_bbu after "Comp1.add((v5_celeb, v5_group, v5_user_email))"
                                        (v55_1, v55_2, v55_3) = (v5_celeb, v5_group, v5_user_email)
                                        if ((v55_1, v55_2) not in _m_Comp1_bbu):
                                            _m_Comp1_bbu[(v55_1, v55_2)] = set()
                                        _m_Comp1_bbu[(v55_1, v55_2)].add(v55_3)
                                        # End maint _m_Comp1_bbu after "Comp1.add((v5_celeb, v5_group, v5_user_email))"
    # End maint Comp1 after "_F_followers.add((u, Set()))"
    u.email = email
    # Begin maint Comp1_d_F_email after "_F_email.add((u, email))"
    # Cost: O(1)
    # Iterate {(v45_user, v45_user_email) : v45_user in Comp1_Tuser1, v45_user in Comp1_Tuser2, (v45_user, v45_user_email) in deltamatch(_F_email, 'bb', _e, 1)}
    (v45_user, v45_user_email) = (u, email)
    if (v45_user in Comp1_Tuser1):
        if (v45_user in Comp1_Tuser2):
            Comp1_d_F_email.add((v45_user, v45_user_email))
    # End maint Comp1_d_F_email after "_F_email.add((u, email))"
    # Begin maint Comp1 after "_F_email.add((u, email))"
    # Cost: O((_U_Comp1_out*Comp1_d_F_followers_in*Comp1_d_M1_in))
    # Iterate {(v11_celeb, v11_group, v11_celeb_followers, v11_user, v11_user_loc, v11_user_email) : (v11_celeb, v11_group) in _U_Comp1, (v11_celeb, v11_celeb_followers) in Comp1_d_F_followers, (v11_celeb_followers, v11_user) in Comp1_d_M1, (v11_group, v11_user) in _M, (v11_user, v11_user_loc) in _F_loc, (v11_user_loc == 'NYC'), (v11_user, v11_user_email) in deltamatch(Comp1_d_F_email, 'bb', _e, 1), (v11_user, v11_user_email) in Comp1_d_F_email}
    (v11_user, v11_user_email) = (u, email)
    if ((v11_user, v11_user_email) in Comp1_d_F_email):
        if hasattr(v11_user, 'loc'):
            v11_user_loc = v11_user.loc
            if (v11_user_loc == 'NYC'):
                for v11_celeb_followers in (_m_Comp1_d_M1_in[v11_user] if (v11_user in _m_Comp1_d_M1_in) else set()):
                    for v11_celeb in (_m_Comp1_d_F_followers_in[v11_celeb_followers] if (v11_celeb_followers in _m_Comp1_d_F_followers_in) else set()):
                        for v11_group in (_m__U_Comp1_out[v11_celeb] if (v11_celeb in _m__U_Comp1_out) else set()):
                            if isinstance(v11_group, Set):
                                if (v11_user in v11_group):
                                    Comp1.add((v11_celeb, v11_group, v11_user_email))
                                    # Begin maint _m_Comp1_bbu after "Comp1.add((v11_celeb, v11_group, v11_user_email))"
                                    (v55_1, v55_2, v55_3) = (v11_celeb, v11_group, v11_user_email)
                                    if ((v55_1, v55_2) not in _m_Comp1_bbu):
                                        _m_Comp1_bbu[(v55_1, v55_2)] = set()
                                    _m_Comp1_bbu[(v55_1, v55_2)].add(v55_3)
                                    # End maint _m_Comp1_bbu after "Comp1.add((v11_celeb, v11_group, v11_user_email))"
    # End maint Comp1 after "_F_email.add((u, email))"
    u.loc = loc
    # Begin maint Comp1_d_F_loc after "_F_loc.add((u, loc))"
    # Cost: O(1)
    # Iterate {(v39_user, v39_user_loc) : v39_user in Comp1_Tuser1, v39_user in Comp1_Tuser2, (v39_user, v39_user_loc) in deltamatch(_F_loc, 'bb', _e, 1)}
    (v39_user, v39_user_loc) = (u, loc)
    if (v39_user in Comp1_Tuser1):
        if (v39_user in Comp1_Tuser2):
            Comp1_d_F_loc.add((v39_user, v39_user_loc))
    # End maint Comp1_d_F_loc after "_F_loc.add((u, loc))"
    # Begin maint Comp1 after "_F_loc.add((u, loc))"
    # Cost: O((_U_Comp1_out*Comp1_d_F_followers_in*Comp1_d_M1_in))
    # Iterate {(v9_celeb, v9_group, v9_celeb_followers, v9_user, v9_user_loc, v9_user_email) : (v9_celeb, v9_group) in _U_Comp1, (v9_celeb, v9_celeb_followers) in Comp1_d_F_followers, (v9_celeb_followers, v9_user) in Comp1_d_M1, (v9_group, v9_user) in _M, (v9_user, v9_user_loc) in deltamatch(Comp1_d_F_loc, 'bb', _e, 1), (v9_user, v9_user_loc) in Comp1_d_F_loc, (v9_user_loc == 'NYC'), (v9_user, v9_user_email) in _F_email}
    (v9_user, v9_user_loc) = (u, loc)
    if ((v9_user, v9_user_loc) in Comp1_d_F_loc):
        if (v9_user_loc == 'NYC'):
            if hasattr(v9_user, 'email'):
                v9_user_email = v9_user.email
                for v9_celeb_followers in (_m_Comp1_d_M1_in[v9_user] if (v9_user in _m_Comp1_d_M1_in) else set()):
                    for v9_celeb in (_m_Comp1_d_F_followers_in[v9_celeb_followers] if (v9_celeb_followers in _m_Comp1_d_F_followers_in) else set()):
                        for v9_group in (_m__U_Comp1_out[v9_celeb] if (v9_celeb in _m__U_Comp1_out) else set()):
                            if isinstance(v9_group, Set):
                                if (v9_user in v9_group):
                                    Comp1.add((v9_celeb, v9_group, v9_user_email))
                                    # Begin maint _m_Comp1_bbu after "Comp1.add((v9_celeb, v9_group, v9_user_email))"
                                    (v55_1, v55_2, v55_3) = (v9_celeb, v9_group, v9_user_email)
                                    if ((v55_1, v55_2) not in _m_Comp1_bbu):
                                        _m_Comp1_bbu[(v55_1, v55_2)] = set()
                                    _m_Comp1_bbu[(v55_1, v55_2)].add(v55_3)
                                    # End maint _m_Comp1_bbu after "Comp1.add((v9_celeb, v9_group, v9_user_email))"
    # End maint Comp1 after "_F_loc.add((u, loc))"
    return u

def make_group():
    # Cost: O(1)
    g = Set()
    return g

def follow(u, c):
    # Cost: O(((_U_Comp1_out*Comp1_d_F_followers_in) + _U_Comp1_in))
    assert (u not in c.followers)
    v1 = c.followers
    v1.add(u)
    # Begin maint Comp1_d_M2 after "_M.add((v1, u))"
    # Cost: O(1)
    # Iterate {(v31_group, v31_user) : v31_group in Comp1_Tgroup, (v31_group, v31_user) in deltamatch(_M, 'bb', _e, 1)}
    (v31_group, v31_user) = (v1, u)
    if (v31_group in Comp1_Tgroup):
        Comp1_d_M2.add((v31_group, v31_user))
        # Begin maint Comp1_Tuser2 after "Comp1_d_M2.add((v31_group, v31_user))"
        # Cost: O(1)
        # Iterate {(v33_group, v33_user) : (v33_group, v33_user) in deltamatch(Comp1_d_M2, 'bb', _e, 1)}
        (v33_group, v33_user) = (v31_group, v31_user)
        if (v33_user not in Comp1_Tuser2):
            Comp1_Tuser2.add(v33_user)
            # Begin maint Comp1_d_F_email after "Comp1_Tuser2.add(v33_user)"
            # Cost: O(1)
            # Iterate {(v43_user, v43_user_email) : v43_user in Comp1_Tuser1, v43_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v43_user, v43_user_email) in _F_email}
            v43_user = v33_user
            if (v43_user in Comp1_Tuser1):
                if hasattr(v43_user, 'email'):
                    v43_user_email = v43_user.email
                    Comp1_d_F_email.add((v43_user, v43_user_email))
            # End maint Comp1_d_F_email after "Comp1_Tuser2.add(v33_user)"
            # Begin maint Comp1_d_F_loc after "Comp1_Tuser2.add(v33_user)"
            # Cost: O(1)
            # Iterate {(v37_user, v37_user_loc) : v37_user in Comp1_Tuser1, v37_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v37_user, v37_user_loc) in _F_loc}
            v37_user = v33_user
            if (v37_user in Comp1_Tuser1):
                if hasattr(v37_user, 'loc'):
                    v37_user_loc = v37_user.loc
                    Comp1_d_F_loc.add((v37_user, v37_user_loc))
            # End maint Comp1_d_F_loc after "Comp1_Tuser2.add(v33_user)"
        else:
            Comp1_Tuser2.incref(v33_user)
        # End maint Comp1_Tuser2 after "Comp1_d_M2.add((v31_group, v31_user))"
    # End maint Comp1_d_M2 after "_M.add((v1, u))"
    # Begin maint Comp1_d_M1 after "_M.add((v1, u))"
    # Cost: O(1)
    # Iterate {(v25_celeb_followers, v25_user) : v25_celeb_followers in Comp1_Tceleb_followers, (v25_celeb_followers, v25_user) in deltamatch(_M, 'bb', _e, 1)}
    (v25_celeb_followers, v25_user) = (v1, u)
    if (v25_celeb_followers in Comp1_Tceleb_followers):
        Comp1_d_M1.add((v25_celeb_followers, v25_user))
        # Begin maint _m_Comp1_d_M1_in after "Comp1_d_M1.add((v25_celeb_followers, v25_user))"
        (v53_1, v53_2) = (v25_celeb_followers, v25_user)
        if (v53_2 not in _m_Comp1_d_M1_in):
            _m_Comp1_d_M1_in[v53_2] = set()
        _m_Comp1_d_M1_in[v53_2].add(v53_1)
        # End maint _m_Comp1_d_M1_in after "Comp1_d_M1.add((v25_celeb_followers, v25_user))"
        # Begin maint Comp1_Tuser1 after "Comp1_d_M1.add((v25_celeb_followers, v25_user))"
        # Cost: O(1)
        # Iterate {(v27_celeb_followers, v27_user) : (v27_celeb_followers, v27_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1)}
        (v27_celeb_followers, v27_user) = (v25_celeb_followers, v25_user)
        if (v27_user not in Comp1_Tuser1):
            Comp1_Tuser1.add(v27_user)
            # Begin maint Comp1_d_F_email after "Comp1_Tuser1.add(v27_user)"
            # Cost: O(1)
            # Iterate {(v41_user, v41_user_email) : v41_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v41_user in Comp1_Tuser2, (v41_user, v41_user_email) in _F_email}
            v41_user = v27_user
            if (v41_user in Comp1_Tuser2):
                if hasattr(v41_user, 'email'):
                    v41_user_email = v41_user.email
                    Comp1_d_F_email.add((v41_user, v41_user_email))
            # End maint Comp1_d_F_email after "Comp1_Tuser1.add(v27_user)"
            # Begin maint Comp1_d_F_loc after "Comp1_Tuser1.add(v27_user)"
            # Cost: O(1)
            # Iterate {(v35_user, v35_user_loc) : v35_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v35_user in Comp1_Tuser2, (v35_user, v35_user_loc) in _F_loc}
            v35_user = v27_user
            if (v35_user in Comp1_Tuser2):
                if hasattr(v35_user, 'loc'):
                    v35_user_loc = v35_user.loc
                    Comp1_d_F_loc.add((v35_user, v35_user_loc))
            # End maint Comp1_d_F_loc after "Comp1_Tuser1.add(v27_user)"
        else:
            Comp1_Tuser1.incref(v27_user)
        # End maint Comp1_Tuser1 after "Comp1_d_M1.add((v25_celeb_followers, v25_user))"
    # End maint Comp1_d_M1 after "_M.add((v1, u))"
    # Begin maint Comp1 after "_M.add((v1, u))"
    # Cost: O(((_U_Comp1_out*Comp1_d_F_followers_in) + _U_Comp1_in))
    # Iterate {(v7_celeb, v7_group, v7_celeb_followers, v7_user, v7_user_loc, v7_user_email) : (v7_celeb, v7_group) in _U_Comp1, (v7_celeb, v7_celeb_followers) in Comp1_d_F_followers, (v7_celeb_followers, v7_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1), (v7_celeb_followers, v7_user) in Comp1_d_M1, (v7_group, v7_user) in (_M - {_e}), (v7_user, v7_user_loc) in _F_loc, (v7_user_loc == 'NYC'), (v7_user, v7_user_email) in _F_email}
    (v7_celeb_followers, v7_user) = (v1, u)
    if ((v7_celeb_followers, v7_user) in Comp1_d_M1):
        if hasattr(v7_user, 'loc'):
            v7_user_loc = v7_user.loc
            if (v7_user_loc == 'NYC'):
                if hasattr(v7_user, 'email'):
                    v7_user_email = v7_user.email
                    for v7_celeb in (_m_Comp1_d_F_followers_in[v7_celeb_followers] if (v7_celeb_followers in _m_Comp1_d_F_followers_in) else set()):
                        for v7_group in (_m__U_Comp1_out[v7_celeb] if (v7_celeb in _m__U_Comp1_out) else set()):
                            if isinstance(v7_group, Set):
                                if (v7_user in v7_group):
                                    if ((v7_group, v7_user) != (v1, u)):
                                        Comp1.add((v7_celeb, v7_group, v7_user_email))
                                        # Begin maint _m_Comp1_bbu after "Comp1.add((v7_celeb, v7_group, v7_user_email))"
                                        (v55_1, v55_2, v55_3) = (v7_celeb, v7_group, v7_user_email)
                                        if ((v55_1, v55_2) not in _m_Comp1_bbu):
                                            _m_Comp1_bbu[(v55_1, v55_2)] = set()
                                        _m_Comp1_bbu[(v55_1, v55_2)].add(v55_3)
                                        # End maint _m_Comp1_bbu after "Comp1.add((v7_celeb, v7_group, v7_user_email))"
    # Iterate {(v7_celeb, v7_group, v7_celeb_followers, v7_user, v7_user_loc, v7_user_email) : (v7_celeb, v7_group) in _U_Comp1, (v7_celeb, v7_celeb_followers) in _F_followers, (v7_celeb_followers, v7_user) in _M, (v7_group, v7_user) in deltamatch(Comp1_d_M2, 'bb', _e, 1), (v7_group, v7_user) in Comp1_d_M2, (v7_user, v7_user_loc) in _F_loc, (v7_user_loc == 'NYC'), (v7_user, v7_user_email) in _F_email}
    (v7_group, v7_user) = (v1, u)
    if ((v7_group, v7_user) in Comp1_d_M2):
        if hasattr(v7_user, 'loc'):
            v7_user_loc = v7_user.loc
            if (v7_user_loc == 'NYC'):
                if hasattr(v7_user, 'email'):
                    v7_user_email = v7_user.email
                    for v7_celeb in (_m__U_Comp1_in[v7_group] if (v7_group in _m__U_Comp1_in) else set()):
                        if hasattr(v7_celeb, 'followers'):
                            v7_celeb_followers = v7_celeb.followers
                            if isinstance(v7_celeb_followers, Set):
                                if (v7_user in v7_celeb_followers):
                                    Comp1.add((v7_celeb, v7_group, v7_user_email))
                                    # Begin maint _m_Comp1_bbu after "Comp1.add((v7_celeb, v7_group, v7_user_email))"
                                    (v55_1, v55_2, v55_3) = (v7_celeb, v7_group, v7_user_email)
                                    if ((v55_1, v55_2) not in _m_Comp1_bbu):
                                        _m_Comp1_bbu[(v55_1, v55_2)] = set()
                                    _m_Comp1_bbu[(v55_1, v55_2)].add(v55_3)
                                    # End maint _m_Comp1_bbu after "Comp1.add((v7_celeb, v7_group, v7_user_email))"
    # End maint Comp1 after "_M.add((v1, u))"

def unfollow(u, c):
    # Cost: O(((_U_Comp1_out*Comp1_d_F_followers_in) + _U_Comp1_in))
    assert (u in c.followers)
    v2 = c.followers
    # Begin maint Comp1 before "_M.remove((v2, u))"
    # Cost: O(((_U_Comp1_out*Comp1_d_F_followers_in) + _U_Comp1_in))
    # Iterate {(v8_celeb, v8_group, v8_celeb_followers, v8_user, v8_user_loc, v8_user_email) : (v8_celeb, v8_group) in _U_Comp1, (v8_celeb, v8_celeb_followers) in Comp1_d_F_followers, (v8_celeb_followers, v8_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1), (v8_celeb_followers, v8_user) in Comp1_d_M1, (v8_group, v8_user) in (_M - {_e}), (v8_user, v8_user_loc) in _F_loc, (v8_user_loc == 'NYC'), (v8_user, v8_user_email) in _F_email}
    (v8_celeb_followers, v8_user) = (v2, u)
    if ((v8_celeb_followers, v8_user) in Comp1_d_M1):
        if hasattr(v8_user, 'loc'):
            v8_user_loc = v8_user.loc
            if (v8_user_loc == 'NYC'):
                if hasattr(v8_user, 'email'):
                    v8_user_email = v8_user.email
                    for v8_celeb in (_m_Comp1_d_F_followers_in[v8_celeb_followers] if (v8_celeb_followers in _m_Comp1_d_F_followers_in) else set()):
                        for v8_group in (_m__U_Comp1_out[v8_celeb] if (v8_celeb in _m__U_Comp1_out) else set()):
                            if isinstance(v8_group, Set):
                                if (v8_user in v8_group):
                                    if ((v8_group, v8_user) != (v2, u)):
                                        # Begin maint _m_Comp1_bbu before "Comp1.remove((v8_celeb, v8_group, v8_user_email))"
                                        (v56_1, v56_2, v56_3) = (v8_celeb, v8_group, v8_user_email)
                                        _m_Comp1_bbu[(v56_1, v56_2)].remove(v56_3)
                                        if (len(_m_Comp1_bbu[(v56_1, v56_2)]) == 0):
                                            del _m_Comp1_bbu[(v56_1, v56_2)]
                                        # End maint _m_Comp1_bbu before "Comp1.remove((v8_celeb, v8_group, v8_user_email))"
                                        Comp1.remove((v8_celeb, v8_group, v8_user_email))
    # Iterate {(v8_celeb, v8_group, v8_celeb_followers, v8_user, v8_user_loc, v8_user_email) : (v8_celeb, v8_group) in _U_Comp1, (v8_celeb, v8_celeb_followers) in _F_followers, (v8_celeb_followers, v8_user) in _M, (v8_group, v8_user) in deltamatch(Comp1_d_M2, 'bb', _e, 1), (v8_group, v8_user) in Comp1_d_M2, (v8_user, v8_user_loc) in _F_loc, (v8_user_loc == 'NYC'), (v8_user, v8_user_email) in _F_email}
    (v8_group, v8_user) = (v2, u)
    if ((v8_group, v8_user) in Comp1_d_M2):
        if hasattr(v8_user, 'loc'):
            v8_user_loc = v8_user.loc
            if (v8_user_loc == 'NYC'):
                if hasattr(v8_user, 'email'):
                    v8_user_email = v8_user.email
                    for v8_celeb in (_m__U_Comp1_in[v8_group] if (v8_group in _m__U_Comp1_in) else set()):
                        if hasattr(v8_celeb, 'followers'):
                            v8_celeb_followers = v8_celeb.followers
                            if isinstance(v8_celeb_followers, Set):
                                if (v8_user in v8_celeb_followers):
                                    # Begin maint _m_Comp1_bbu before "Comp1.remove((v8_celeb, v8_group, v8_user_email))"
                                    (v56_1, v56_2, v56_3) = (v8_celeb, v8_group, v8_user_email)
                                    _m_Comp1_bbu[(v56_1, v56_2)].remove(v56_3)
                                    if (len(_m_Comp1_bbu[(v56_1, v56_2)]) == 0):
                                        del _m_Comp1_bbu[(v56_1, v56_2)]
                                    # End maint _m_Comp1_bbu before "Comp1.remove((v8_celeb, v8_group, v8_user_email))"
                                    Comp1.remove((v8_celeb, v8_group, v8_user_email))
    # End maint Comp1 before "_M.remove((v2, u))"
    # Begin maint Comp1_d_M1 before "_M.remove((v2, u))"
    # Cost: O(1)
    # Iterate {(v26_celeb_followers, v26_user) : v26_celeb_followers in Comp1_Tceleb_followers, (v26_celeb_followers, v26_user) in deltamatch(_M, 'bb', _e, 1)}
    (v26_celeb_followers, v26_user) = (v2, u)
    if (v26_celeb_followers in Comp1_Tceleb_followers):
        # Begin maint Comp1_Tuser1 before "Comp1_d_M1.remove((v26_celeb_followers, v26_user))"
        # Cost: O(1)
        # Iterate {(v28_celeb_followers, v28_user) : (v28_celeb_followers, v28_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1)}
        (v28_celeb_followers, v28_user) = (v26_celeb_followers, v26_user)
        if (Comp1_Tuser1.getref(v28_user) == 1):
            # Begin maint Comp1_d_F_loc before "Comp1_Tuser1.remove(v28_user)"
            # Cost: O(1)
            # Iterate {(v36_user, v36_user_loc) : v36_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v36_user in Comp1_Tuser2, (v36_user, v36_user_loc) in _F_loc}
            v36_user = v28_user
            if (v36_user in Comp1_Tuser2):
                if hasattr(v36_user, 'loc'):
                    v36_user_loc = v36_user.loc
                    Comp1_d_F_loc.remove((v36_user, v36_user_loc))
            # End maint Comp1_d_F_loc before "Comp1_Tuser1.remove(v28_user)"
            # Begin maint Comp1_d_F_email before "Comp1_Tuser1.remove(v28_user)"
            # Cost: O(1)
            # Iterate {(v42_user, v42_user_email) : v42_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v42_user in Comp1_Tuser2, (v42_user, v42_user_email) in _F_email}
            v42_user = v28_user
            if (v42_user in Comp1_Tuser2):
                if hasattr(v42_user, 'email'):
                    v42_user_email = v42_user.email
                    Comp1_d_F_email.remove((v42_user, v42_user_email))
            # End maint Comp1_d_F_email before "Comp1_Tuser1.remove(v28_user)"
            Comp1_Tuser1.remove(v28_user)
        else:
            Comp1_Tuser1.decref(v28_user)
        # End maint Comp1_Tuser1 before "Comp1_d_M1.remove((v26_celeb_followers, v26_user))"
        # Begin maint _m_Comp1_d_M1_in before "Comp1_d_M1.remove((v26_celeb_followers, v26_user))"
        (v54_1, v54_2) = (v26_celeb_followers, v26_user)
        _m_Comp1_d_M1_in[v54_2].remove(v54_1)
        if (len(_m_Comp1_d_M1_in[v54_2]) == 0):
            del _m_Comp1_d_M1_in[v54_2]
        # End maint _m_Comp1_d_M1_in before "Comp1_d_M1.remove((v26_celeb_followers, v26_user))"
        Comp1_d_M1.remove((v26_celeb_followers, v26_user))
    # End maint Comp1_d_M1 before "_M.remove((v2, u))"
    # Begin maint Comp1_d_M2 before "_M.remove((v2, u))"
    # Cost: O(1)
    # Iterate {(v32_group, v32_user) : v32_group in Comp1_Tgroup, (v32_group, v32_user) in deltamatch(_M, 'bb', _e, 1)}
    (v32_group, v32_user) = (v2, u)
    if (v32_group in Comp1_Tgroup):
        # Begin maint Comp1_Tuser2 before "Comp1_d_M2.remove((v32_group, v32_user))"
        # Cost: O(1)
        # Iterate {(v34_group, v34_user) : (v34_group, v34_user) in deltamatch(Comp1_d_M2, 'bb', _e, 1)}
        (v34_group, v34_user) = (v32_group, v32_user)
        if (Comp1_Tuser2.getref(v34_user) == 1):
            # Begin maint Comp1_d_F_loc before "Comp1_Tuser2.remove(v34_user)"
            # Cost: O(1)
            # Iterate {(v38_user, v38_user_loc) : v38_user in Comp1_Tuser1, v38_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v38_user, v38_user_loc) in _F_loc}
            v38_user = v34_user
            if (v38_user in Comp1_Tuser1):
                if hasattr(v38_user, 'loc'):
                    v38_user_loc = v38_user.loc
                    Comp1_d_F_loc.remove((v38_user, v38_user_loc))
            # End maint Comp1_d_F_loc before "Comp1_Tuser2.remove(v34_user)"
            # Begin maint Comp1_d_F_email before "Comp1_Tuser2.remove(v34_user)"
            # Cost: O(1)
            # Iterate {(v44_user, v44_user_email) : v44_user in Comp1_Tuser1, v44_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v44_user, v44_user_email) in _F_email}
            v44_user = v34_user
            if (v44_user in Comp1_Tuser1):
                if hasattr(v44_user, 'email'):
                    v44_user_email = v44_user.email
                    Comp1_d_F_email.remove((v44_user, v44_user_email))
            # End maint Comp1_d_F_email before "Comp1_Tuser2.remove(v34_user)"
            Comp1_Tuser2.remove(v34_user)
        else:
            Comp1_Tuser2.decref(v34_user)
        # End maint Comp1_Tuser2 before "Comp1_d_M2.remove((v32_group, v32_user))"
        Comp1_d_M2.remove((v32_group, v32_user))
    # End maint Comp1_d_M2 before "_M.remove((v2, u))"
    v2.remove(u)

def join_group(u, g):
    # Cost: O(((_U_Comp1_out*Comp1_d_F_followers_in) + _U_Comp1_in))
    assert (u not in g)
    g.add(u)
    # Begin maint Comp1_d_M2 after "_M.add((g, u))"
    # Cost: O(1)
    # Iterate {(v31_group, v31_user) : v31_group in Comp1_Tgroup, (v31_group, v31_user) in deltamatch(_M, 'bb', _e, 1)}
    (v31_group, v31_user) = (g, u)
    if (v31_group in Comp1_Tgroup):
        Comp1_d_M2.add((v31_group, v31_user))
        # Begin maint Comp1_Tuser2 after "Comp1_d_M2.add((v31_group, v31_user))"
        # Cost: O(1)
        # Iterate {(v33_group, v33_user) : (v33_group, v33_user) in deltamatch(Comp1_d_M2, 'bb', _e, 1)}
        (v33_group, v33_user) = (v31_group, v31_user)
        if (v33_user not in Comp1_Tuser2):
            Comp1_Tuser2.add(v33_user)
            # Begin maint Comp1_d_F_email after "Comp1_Tuser2.add(v33_user)"
            # Cost: O(1)
            # Iterate {(v43_user, v43_user_email) : v43_user in Comp1_Tuser1, v43_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v43_user, v43_user_email) in _F_email}
            v43_user = v33_user
            if (v43_user in Comp1_Tuser1):
                if hasattr(v43_user, 'email'):
                    v43_user_email = v43_user.email
                    Comp1_d_F_email.add((v43_user, v43_user_email))
            # End maint Comp1_d_F_email after "Comp1_Tuser2.add(v33_user)"
            # Begin maint Comp1_d_F_loc after "Comp1_Tuser2.add(v33_user)"
            # Cost: O(1)
            # Iterate {(v37_user, v37_user_loc) : v37_user in Comp1_Tuser1, v37_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v37_user, v37_user_loc) in _F_loc}
            v37_user = v33_user
            if (v37_user in Comp1_Tuser1):
                if hasattr(v37_user, 'loc'):
                    v37_user_loc = v37_user.loc
                    Comp1_d_F_loc.add((v37_user, v37_user_loc))
            # End maint Comp1_d_F_loc after "Comp1_Tuser2.add(v33_user)"
        else:
            Comp1_Tuser2.incref(v33_user)
        # End maint Comp1_Tuser2 after "Comp1_d_M2.add((v31_group, v31_user))"
    # End maint Comp1_d_M2 after "_M.add((g, u))"
    # Begin maint Comp1_d_M1 after "_M.add((g, u))"
    # Cost: O(1)
    # Iterate {(v25_celeb_followers, v25_user) : v25_celeb_followers in Comp1_Tceleb_followers, (v25_celeb_followers, v25_user) in deltamatch(_M, 'bb', _e, 1)}
    (v25_celeb_followers, v25_user) = (g, u)
    if (v25_celeb_followers in Comp1_Tceleb_followers):
        Comp1_d_M1.add((v25_celeb_followers, v25_user))
        # Begin maint _m_Comp1_d_M1_in after "Comp1_d_M1.add((v25_celeb_followers, v25_user))"
        (v53_1, v53_2) = (v25_celeb_followers, v25_user)
        if (v53_2 not in _m_Comp1_d_M1_in):
            _m_Comp1_d_M1_in[v53_2] = set()
        _m_Comp1_d_M1_in[v53_2].add(v53_1)
        # End maint _m_Comp1_d_M1_in after "Comp1_d_M1.add((v25_celeb_followers, v25_user))"
        # Begin maint Comp1_Tuser1 after "Comp1_d_M1.add((v25_celeb_followers, v25_user))"
        # Cost: O(1)
        # Iterate {(v27_celeb_followers, v27_user) : (v27_celeb_followers, v27_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1)}
        (v27_celeb_followers, v27_user) = (v25_celeb_followers, v25_user)
        if (v27_user not in Comp1_Tuser1):
            Comp1_Tuser1.add(v27_user)
            # Begin maint Comp1_d_F_email after "Comp1_Tuser1.add(v27_user)"
            # Cost: O(1)
            # Iterate {(v41_user, v41_user_email) : v41_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v41_user in Comp1_Tuser2, (v41_user, v41_user_email) in _F_email}
            v41_user = v27_user
            if (v41_user in Comp1_Tuser2):
                if hasattr(v41_user, 'email'):
                    v41_user_email = v41_user.email
                    Comp1_d_F_email.add((v41_user, v41_user_email))
            # End maint Comp1_d_F_email after "Comp1_Tuser1.add(v27_user)"
            # Begin maint Comp1_d_F_loc after "Comp1_Tuser1.add(v27_user)"
            # Cost: O(1)
            # Iterate {(v35_user, v35_user_loc) : v35_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v35_user in Comp1_Tuser2, (v35_user, v35_user_loc) in _F_loc}
            v35_user = v27_user
            if (v35_user in Comp1_Tuser2):
                if hasattr(v35_user, 'loc'):
                    v35_user_loc = v35_user.loc
                    Comp1_d_F_loc.add((v35_user, v35_user_loc))
            # End maint Comp1_d_F_loc after "Comp1_Tuser1.add(v27_user)"
        else:
            Comp1_Tuser1.incref(v27_user)
        # End maint Comp1_Tuser1 after "Comp1_d_M1.add((v25_celeb_followers, v25_user))"
    # End maint Comp1_d_M1 after "_M.add((g, u))"
    # Begin maint Comp1 after "_M.add((g, u))"
    # Cost: O(((_U_Comp1_out*Comp1_d_F_followers_in) + _U_Comp1_in))
    # Iterate {(v7_celeb, v7_group, v7_celeb_followers, v7_user, v7_user_loc, v7_user_email) : (v7_celeb, v7_group) in _U_Comp1, (v7_celeb, v7_celeb_followers) in Comp1_d_F_followers, (v7_celeb_followers, v7_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1), (v7_celeb_followers, v7_user) in Comp1_d_M1, (v7_group, v7_user) in (_M - {_e}), (v7_user, v7_user_loc) in _F_loc, (v7_user_loc == 'NYC'), (v7_user, v7_user_email) in _F_email}
    (v7_celeb_followers, v7_user) = (g, u)
    if ((v7_celeb_followers, v7_user) in Comp1_d_M1):
        if hasattr(v7_user, 'loc'):
            v7_user_loc = v7_user.loc
            if (v7_user_loc == 'NYC'):
                if hasattr(v7_user, 'email'):
                    v7_user_email = v7_user.email
                    for v7_celeb in (_m_Comp1_d_F_followers_in[v7_celeb_followers] if (v7_celeb_followers in _m_Comp1_d_F_followers_in) else set()):
                        for v7_group in (_m__U_Comp1_out[v7_celeb] if (v7_celeb in _m__U_Comp1_out) else set()):
                            if isinstance(v7_group, Set):
                                if (v7_user in v7_group):
                                    if ((v7_group, v7_user) != (g, u)):
                                        Comp1.add((v7_celeb, v7_group, v7_user_email))
                                        # Begin maint _m_Comp1_bbu after "Comp1.add((v7_celeb, v7_group, v7_user_email))"
                                        (v55_1, v55_2, v55_3) = (v7_celeb, v7_group, v7_user_email)
                                        if ((v55_1, v55_2) not in _m_Comp1_bbu):
                                            _m_Comp1_bbu[(v55_1, v55_2)] = set()
                                        _m_Comp1_bbu[(v55_1, v55_2)].add(v55_3)
                                        # End maint _m_Comp1_bbu after "Comp1.add((v7_celeb, v7_group, v7_user_email))"
    # Iterate {(v7_celeb, v7_group, v7_celeb_followers, v7_user, v7_user_loc, v7_user_email) : (v7_celeb, v7_group) in _U_Comp1, (v7_celeb, v7_celeb_followers) in _F_followers, (v7_celeb_followers, v7_user) in _M, (v7_group, v7_user) in deltamatch(Comp1_d_M2, 'bb', _e, 1), (v7_group, v7_user) in Comp1_d_M2, (v7_user, v7_user_loc) in _F_loc, (v7_user_loc == 'NYC'), (v7_user, v7_user_email) in _F_email}
    (v7_group, v7_user) = (g, u)
    if ((v7_group, v7_user) in Comp1_d_M2):
        if hasattr(v7_user, 'loc'):
            v7_user_loc = v7_user.loc
            if (v7_user_loc == 'NYC'):
                if hasattr(v7_user, 'email'):
                    v7_user_email = v7_user.email
                    for v7_celeb in (_m__U_Comp1_in[v7_group] if (v7_group in _m__U_Comp1_in) else set()):
                        if hasattr(v7_celeb, 'followers'):
                            v7_celeb_followers = v7_celeb.followers
                            if isinstance(v7_celeb_followers, Set):
                                if (v7_user in v7_celeb_followers):
                                    Comp1.add((v7_celeb, v7_group, v7_user_email))
                                    # Begin maint _m_Comp1_bbu after "Comp1.add((v7_celeb, v7_group, v7_user_email))"
                                    (v55_1, v55_2, v55_3) = (v7_celeb, v7_group, v7_user_email)
                                    if ((v55_1, v55_2) not in _m_Comp1_bbu):
                                        _m_Comp1_bbu[(v55_1, v55_2)] = set()
                                    _m_Comp1_bbu[(v55_1, v55_2)].add(v55_3)
                                    # End maint _m_Comp1_bbu after "Comp1.add((v7_celeb, v7_group, v7_user_email))"
    # End maint Comp1 after "_M.add((g, u))"

def leave_group(u, g):
    # Cost: O(((_U_Comp1_out*Comp1_d_F_followers_in) + _U_Comp1_in))
    assert (u in g)
    # Begin maint Comp1 before "_M.remove((g, u))"
    # Cost: O(((_U_Comp1_out*Comp1_d_F_followers_in) + _U_Comp1_in))
    # Iterate {(v8_celeb, v8_group, v8_celeb_followers, v8_user, v8_user_loc, v8_user_email) : (v8_celeb, v8_group) in _U_Comp1, (v8_celeb, v8_celeb_followers) in Comp1_d_F_followers, (v8_celeb_followers, v8_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1), (v8_celeb_followers, v8_user) in Comp1_d_M1, (v8_group, v8_user) in (_M - {_e}), (v8_user, v8_user_loc) in _F_loc, (v8_user_loc == 'NYC'), (v8_user, v8_user_email) in _F_email}
    (v8_celeb_followers, v8_user) = (g, u)
    if ((v8_celeb_followers, v8_user) in Comp1_d_M1):
        if hasattr(v8_user, 'loc'):
            v8_user_loc = v8_user.loc
            if (v8_user_loc == 'NYC'):
                if hasattr(v8_user, 'email'):
                    v8_user_email = v8_user.email
                    for v8_celeb in (_m_Comp1_d_F_followers_in[v8_celeb_followers] if (v8_celeb_followers in _m_Comp1_d_F_followers_in) else set()):
                        for v8_group in (_m__U_Comp1_out[v8_celeb] if (v8_celeb in _m__U_Comp1_out) else set()):
                            if isinstance(v8_group, Set):
                                if (v8_user in v8_group):
                                    if ((v8_group, v8_user) != (g, u)):
                                        # Begin maint _m_Comp1_bbu before "Comp1.remove((v8_celeb, v8_group, v8_user_email))"
                                        (v56_1, v56_2, v56_3) = (v8_celeb, v8_group, v8_user_email)
                                        _m_Comp1_bbu[(v56_1, v56_2)].remove(v56_3)
                                        if (len(_m_Comp1_bbu[(v56_1, v56_2)]) == 0):
                                            del _m_Comp1_bbu[(v56_1, v56_2)]
                                        # End maint _m_Comp1_bbu before "Comp1.remove((v8_celeb, v8_group, v8_user_email))"
                                        Comp1.remove((v8_celeb, v8_group, v8_user_email))
    # Iterate {(v8_celeb, v8_group, v8_celeb_followers, v8_user, v8_user_loc, v8_user_email) : (v8_celeb, v8_group) in _U_Comp1, (v8_celeb, v8_celeb_followers) in _F_followers, (v8_celeb_followers, v8_user) in _M, (v8_group, v8_user) in deltamatch(Comp1_d_M2, 'bb', _e, 1), (v8_group, v8_user) in Comp1_d_M2, (v8_user, v8_user_loc) in _F_loc, (v8_user_loc == 'NYC'), (v8_user, v8_user_email) in _F_email}
    (v8_group, v8_user) = (g, u)
    if ((v8_group, v8_user) in Comp1_d_M2):
        if hasattr(v8_user, 'loc'):
            v8_user_loc = v8_user.loc
            if (v8_user_loc == 'NYC'):
                if hasattr(v8_user, 'email'):
                    v8_user_email = v8_user.email
                    for v8_celeb in (_m__U_Comp1_in[v8_group] if (v8_group in _m__U_Comp1_in) else set()):
                        if hasattr(v8_celeb, 'followers'):
                            v8_celeb_followers = v8_celeb.followers
                            if isinstance(v8_celeb_followers, Set):
                                if (v8_user in v8_celeb_followers):
                                    # Begin maint _m_Comp1_bbu before "Comp1.remove((v8_celeb, v8_group, v8_user_email))"
                                    (v56_1, v56_2, v56_3) = (v8_celeb, v8_group, v8_user_email)
                                    _m_Comp1_bbu[(v56_1, v56_2)].remove(v56_3)
                                    if (len(_m_Comp1_bbu[(v56_1, v56_2)]) == 0):
                                        del _m_Comp1_bbu[(v56_1, v56_2)]
                                    # End maint _m_Comp1_bbu before "Comp1.remove((v8_celeb, v8_group, v8_user_email))"
                                    Comp1.remove((v8_celeb, v8_group, v8_user_email))
    # End maint Comp1 before "_M.remove((g, u))"
    # Begin maint Comp1_d_M1 before "_M.remove((g, u))"
    # Cost: O(1)
    # Iterate {(v26_celeb_followers, v26_user) : v26_celeb_followers in Comp1_Tceleb_followers, (v26_celeb_followers, v26_user) in deltamatch(_M, 'bb', _e, 1)}
    (v26_celeb_followers, v26_user) = (g, u)
    if (v26_celeb_followers in Comp1_Tceleb_followers):
        # Begin maint Comp1_Tuser1 before "Comp1_d_M1.remove((v26_celeb_followers, v26_user))"
        # Cost: O(1)
        # Iterate {(v28_celeb_followers, v28_user) : (v28_celeb_followers, v28_user) in deltamatch(Comp1_d_M1, 'bb', _e, 1)}
        (v28_celeb_followers, v28_user) = (v26_celeb_followers, v26_user)
        if (Comp1_Tuser1.getref(v28_user) == 1):
            # Begin maint Comp1_d_F_loc before "Comp1_Tuser1.remove(v28_user)"
            # Cost: O(1)
            # Iterate {(v36_user, v36_user_loc) : v36_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v36_user in Comp1_Tuser2, (v36_user, v36_user_loc) in _F_loc}
            v36_user = v28_user
            if (v36_user in Comp1_Tuser2):
                if hasattr(v36_user, 'loc'):
                    v36_user_loc = v36_user.loc
                    Comp1_d_F_loc.remove((v36_user, v36_user_loc))
            # End maint Comp1_d_F_loc before "Comp1_Tuser1.remove(v28_user)"
            # Begin maint Comp1_d_F_email before "Comp1_Tuser1.remove(v28_user)"
            # Cost: O(1)
            # Iterate {(v42_user, v42_user_email) : v42_user in deltamatch(Comp1_Tuser1, 'b', _e, 1), v42_user in Comp1_Tuser2, (v42_user, v42_user_email) in _F_email}
            v42_user = v28_user
            if (v42_user in Comp1_Tuser2):
                if hasattr(v42_user, 'email'):
                    v42_user_email = v42_user.email
                    Comp1_d_F_email.remove((v42_user, v42_user_email))
            # End maint Comp1_d_F_email before "Comp1_Tuser1.remove(v28_user)"
            Comp1_Tuser1.remove(v28_user)
        else:
            Comp1_Tuser1.decref(v28_user)
        # End maint Comp1_Tuser1 before "Comp1_d_M1.remove((v26_celeb_followers, v26_user))"
        # Begin maint _m_Comp1_d_M1_in before "Comp1_d_M1.remove((v26_celeb_followers, v26_user))"
        (v54_1, v54_2) = (v26_celeb_followers, v26_user)
        _m_Comp1_d_M1_in[v54_2].remove(v54_1)
        if (len(_m_Comp1_d_M1_in[v54_2]) == 0):
            del _m_Comp1_d_M1_in[v54_2]
        # End maint _m_Comp1_d_M1_in before "Comp1_d_M1.remove((v26_celeb_followers, v26_user))"
        Comp1_d_M1.remove((v26_celeb_followers, v26_user))
    # End maint Comp1_d_M1 before "_M.remove((g, u))"
    # Begin maint Comp1_d_M2 before "_M.remove((g, u))"
    # Cost: O(1)
    # Iterate {(v32_group, v32_user) : v32_group in Comp1_Tgroup, (v32_group, v32_user) in deltamatch(_M, 'bb', _e, 1)}
    (v32_group, v32_user) = (g, u)
    if (v32_group in Comp1_Tgroup):
        # Begin maint Comp1_Tuser2 before "Comp1_d_M2.remove((v32_group, v32_user))"
        # Cost: O(1)
        # Iterate {(v34_group, v34_user) : (v34_group, v34_user) in deltamatch(Comp1_d_M2, 'bb', _e, 1)}
        (v34_group, v34_user) = (v32_group, v32_user)
        if (Comp1_Tuser2.getref(v34_user) == 1):
            # Begin maint Comp1_d_F_loc before "Comp1_Tuser2.remove(v34_user)"
            # Cost: O(1)
            # Iterate {(v38_user, v38_user_loc) : v38_user in Comp1_Tuser1, v38_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v38_user, v38_user_loc) in _F_loc}
            v38_user = v34_user
            if (v38_user in Comp1_Tuser1):
                if hasattr(v38_user, 'loc'):
                    v38_user_loc = v38_user.loc
                    Comp1_d_F_loc.remove((v38_user, v38_user_loc))
            # End maint Comp1_d_F_loc before "Comp1_Tuser2.remove(v34_user)"
            # Begin maint Comp1_d_F_email before "Comp1_Tuser2.remove(v34_user)"
            # Cost: O(1)
            # Iterate {(v44_user, v44_user_email) : v44_user in Comp1_Tuser1, v44_user in deltamatch(Comp1_Tuser2, 'b', _e, 1), (v44_user, v44_user_email) in _F_email}
            v44_user = v34_user
            if (v44_user in Comp1_Tuser1):
                if hasattr(v44_user, 'email'):
                    v44_user_email = v44_user.email
                    Comp1_d_F_email.remove((v44_user, v44_user_email))
            # End maint Comp1_d_F_email before "Comp1_Tuser2.remove(v34_user)"
            Comp1_Tuser2.remove(v34_user)
        else:
            Comp1_Tuser2.decref(v34_user)
        # End maint Comp1_Tuser2 before "Comp1_d_M2.remove((v32_group, v32_user))"
        Comp1_d_M2.remove((v32_group, v32_user))
    # End maint Comp1_d_M2 before "_M.remove((g, u))"
    g.remove(u)

def change_loc(u, loc):
    # Cost: O((_U_Comp1_out*Comp1_d_F_followers_in*Comp1_d_M1_in))
    # Begin maint Comp1 before "_F_loc.remove((u, u.loc))"
    # Cost: O((_U_Comp1_out*Comp1_d_F_followers_in*Comp1_d_M1_in))
    # Iterate {(v10_celeb, v10_group, v10_celeb_followers, v10_user, v10_user_loc, v10_user_email) : (v10_celeb, v10_group) in _U_Comp1, (v10_celeb, v10_celeb_followers) in Comp1_d_F_followers, (v10_celeb_followers, v10_user) in Comp1_d_M1, (v10_group, v10_user) in _M, (v10_user, v10_user_loc) in deltamatch(Comp1_d_F_loc, 'bb', _e, 1), (v10_user, v10_user_loc) in Comp1_d_F_loc, (v10_user_loc == 'NYC'), (v10_user, v10_user_email) in _F_email}
    (v10_user, v10_user_loc) = (u, u.loc)
    if ((v10_user, v10_user_loc) in Comp1_d_F_loc):
        if (v10_user_loc == 'NYC'):
            if hasattr(v10_user, 'email'):
                v10_user_email = v10_user.email
                for v10_celeb_followers in (_m_Comp1_d_M1_in[v10_user] if (v10_user in _m_Comp1_d_M1_in) else set()):
                    for v10_celeb in (_m_Comp1_d_F_followers_in[v10_celeb_followers] if (v10_celeb_followers in _m_Comp1_d_F_followers_in) else set()):
                        for v10_group in (_m__U_Comp1_out[v10_celeb] if (v10_celeb in _m__U_Comp1_out) else set()):
                            if isinstance(v10_group, Set):
                                if (v10_user in v10_group):
                                    # Begin maint _m_Comp1_bbu before "Comp1.remove((v10_celeb, v10_group, v10_user_email))"
                                    (v56_1, v56_2, v56_3) = (v10_celeb, v10_group, v10_user_email)
                                    _m_Comp1_bbu[(v56_1, v56_2)].remove(v56_3)
                                    if (len(_m_Comp1_bbu[(v56_1, v56_2)]) == 0):
                                        del _m_Comp1_bbu[(v56_1, v56_2)]
                                    # End maint _m_Comp1_bbu before "Comp1.remove((v10_celeb, v10_group, v10_user_email))"
                                    Comp1.remove((v10_celeb, v10_group, v10_user_email))
    # End maint Comp1 before "_F_loc.remove((u, u.loc))"
    # Begin maint Comp1_d_F_loc before "_F_loc.remove((u, u.loc))"
    # Cost: O(1)
    # Iterate {(v40_user, v40_user_loc) : v40_user in Comp1_Tuser1, v40_user in Comp1_Tuser2, (v40_user, v40_user_loc) in deltamatch(_F_loc, 'bb', _e, 1)}
    (v40_user, v40_user_loc) = (u, u.loc)
    if (v40_user in Comp1_Tuser1):
        if (v40_user in Comp1_Tuser2):
            Comp1_d_F_loc.remove((v40_user, v40_user_loc))
    # End maint Comp1_d_F_loc before "_F_loc.remove((u, u.loc))"
    del u.loc
    u.loc = loc
    # Begin maint Comp1_d_F_loc after "_F_loc.add((u, loc))"
    # Cost: O(1)
    # Iterate {(v39_user, v39_user_loc) : v39_user in Comp1_Tuser1, v39_user in Comp1_Tuser2, (v39_user, v39_user_loc) in deltamatch(_F_loc, 'bb', _e, 1)}
    (v39_user, v39_user_loc) = (u, loc)
    if (v39_user in Comp1_Tuser1):
        if (v39_user in Comp1_Tuser2):
            Comp1_d_F_loc.add((v39_user, v39_user_loc))
    # End maint Comp1_d_F_loc after "_F_loc.add((u, loc))"
    # Begin maint Comp1 after "_F_loc.add((u, loc))"
    # Cost: O((_U_Comp1_out*Comp1_d_F_followers_in*Comp1_d_M1_in))
    # Iterate {(v9_celeb, v9_group, v9_celeb_followers, v9_user, v9_user_loc, v9_user_email) : (v9_celeb, v9_group) in _U_Comp1, (v9_celeb, v9_celeb_followers) in Comp1_d_F_followers, (v9_celeb_followers, v9_user) in Comp1_d_M1, (v9_group, v9_user) in _M, (v9_user, v9_user_loc) in deltamatch(Comp1_d_F_loc, 'bb', _e, 1), (v9_user, v9_user_loc) in Comp1_d_F_loc, (v9_user_loc == 'NYC'), (v9_user, v9_user_email) in _F_email}
    (v9_user, v9_user_loc) = (u, loc)
    if ((v9_user, v9_user_loc) in Comp1_d_F_loc):
        if (v9_user_loc == 'NYC'):
            if hasattr(v9_user, 'email'):
                v9_user_email = v9_user.email
                for v9_celeb_followers in (_m_Comp1_d_M1_in[v9_user] if (v9_user in _m_Comp1_d_M1_in) else set()):
                    for v9_celeb in (_m_Comp1_d_F_followers_in[v9_celeb_followers] if (v9_celeb_followers in _m_Comp1_d_F_followers_in) else set()):
                        for v9_group in (_m__U_Comp1_out[v9_celeb] if (v9_celeb in _m__U_Comp1_out) else set()):
                            if isinstance(v9_group, Set):
                                if (v9_user in v9_group):
                                    Comp1.add((v9_celeb, v9_group, v9_user_email))
                                    # Begin maint _m_Comp1_bbu after "Comp1.add((v9_celeb, v9_group, v9_user_email))"
                                    (v55_1, v55_2, v55_3) = (v9_celeb, v9_group, v9_user_email)
                                    if ((v55_1, v55_2) not in _m_Comp1_bbu):
                                        _m_Comp1_bbu[(v55_1, v55_2)] = set()
                                    _m_Comp1_bbu[(v55_1, v55_2)].add(v55_3)
                                    # End maint _m_Comp1_bbu after "Comp1.add((v9_celeb, v9_group, v9_user_email))"
    # End maint Comp1 after "_F_loc.add((u, loc))"

def do_query(celeb, group):
    # Cost: O((v29_group + v23_celeb_followers + v3_celeb_followers))
    return (query_Comp1(celeb, group) and (_m_Comp1_bbu[(celeb, group)] if ((celeb, group) in _m_Comp1_bbu) else set()))

def do_query_nodemand(celeb, group):
    # Cost: O(1)
    return (_m_Comp1_bbu[(celeb, group)] if ((celeb, group) in _m_Comp1_bbu) else set())
