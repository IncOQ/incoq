# Manually modified version of twitter_dem_tcelim.py.
# Areas where code was deleted are marked with ### comments.
#
# Changed the follow()/unfollow() and join_group()/leave_group()
# functions so that maintenance code for groups in the former and
# celebs in the latter is eliminated, under the assumption that
# follower sets and groups are never alisaed. This includes both
# query maintenance code and demand propagation code.
#
# In addition, eliminated maintenance code in the make_user()
# constructor.

# Q : celeb, group -> {(celeb, group, user_email) for (celeb, group) in REL(_U_Q) for (celeb, celeb_followers) in F(followers) for (celeb_followers, user) in M() for (group, user) in M() for (user, user_loc) in F(loc) if (user_loc == 'NYC') for (user, user_email) in F(email)} : {(Bottom, Bottom, Top)}
# Q_T_celeb : {(celeb,) for (celeb, group) in REL(_U_Q)} : Bottom
# Q_T_group : {(group,) for (celeb, group) in REL(_U_Q)} : Bottom
# Q_d_F_followers : {(celeb, celeb_followers) for (celeb,) in REL(R_Q_T_celeb) for (celeb, celeb_followers) in F(followers)} : Bottom
# Q_T_celeb_followers : {(celeb_followers,) for (celeb, celeb_followers) in REL(R_Q_d_F_followers)} : Bottom
# Q_d_M_1 : {(celeb_followers, user) for (celeb_followers,) in REL(R_Q_T_celeb_followers) for (celeb_followers, user) in M()} : Bottom
# Q_T_user_1 : {(user,) for (celeb_followers, user) in REL(R_Q_d_M_1)} : Bottom
# Q_d_M_2 : {(group, user) for (group,) in REL(R_Q_T_group) for (group, user) in M()} : Bottom
# Q_T_user_2 : {(user,) for (group, user) in REL(R_Q_d_M_2)} : Bottom
# Q_d_F_loc : {(user, user_loc) for (user,) in REL(R_Q_T_user_1) for (user,) in REL(R_Q_T_user_2) for (user, user_loc) in F(loc)} : Bottom
# Q_d_F_email : {(user, user_email) for (user,) in REL(R_Q_T_user_1) for (user,) in REL(R_Q_T_user_2) for (user, user_email) in F(email)} : Bottom
from incoq.mars.runtime import *
# _U_Q : {(Bottom, Bottom)}
_U_Q = Set()
# R_Q_T_celeb : Bottom
R_Q_T_celeb = CSet()
# R_Q_T_group : Bottom
R_Q_T_group = CSet()
# R_Q_d_F_followers : Bottom
R_Q_d_F_followers = Set()
# R_Q_T_celeb_followers : Bottom
R_Q_T_celeb_followers = CSet()
# R_Q_d_M_1 : Bottom
R_Q_d_M_1 = Set()
# R_Q_T_user_1 : Bottom
R_Q_T_user_1 = CSet()
# R_Q_d_M_2 : Bottom
R_Q_d_M_2 = Set()
# R_Q_T_user_2 : Bottom
R_Q_T_user_2 = CSet()
# R_Q_d_F_loc : Bottom
R_Q_d_F_loc = Set()
# R_Q_d_F_email : Bottom
R_Q_d_F_email = Set()
# _U_Q_bu : {Bottom: {Bottom}}
_U_Q_bu = Map()
# R_Q_d_F_followers_ub : {Bottom: {Bottom}}
R_Q_d_F_followers_ub = Map()
# _U_Q_ub : {Bottom: {Bottom}}
_U_Q_ub = Map()
# R_Q_d_M_1_ub : {Bottom: {Bottom}}
R_Q_d_M_1_ub = Map()
# R_Q_bbu : {(Bottom, Bottom): {Top}}
R_Q_bbu = Map()
def _demand_Q(_elem):
    if (_elem not in _U_Q):
        _U_Q.add(_elem)
        # Begin inlined _maint__U_Q_bu_for__U_Q_add.
        (_i47_elem,) = (_elem,)
        (_i47_elem_v1, _i47_elem_v2) = _i47_elem
        _i47_v54_key = _i47_elem_v1
        _i47_v54_value = _i47_elem_v2
        if (_i47_v54_key not in _U_Q_bu):
            _i47_v55 = Set()
            _U_Q_bu[_i47_v54_key] = _i47_v55
        _U_Q_bu[_i47_v54_key].add(_i47_v54_value)
        # End inlined _maint__U_Q_bu_for__U_Q_add.
        # Begin inlined _maint__U_Q_ub_for__U_Q_add.
        (_i48_elem,) = (_elem,)
        (_i48_elem_v1, _i48_elem_v2) = _i48_elem
        _i48_v57_key = _i48_elem_v2
        _i48_v57_value = _i48_elem_v1
        if (_i48_v57_key not in _U_Q_ub):
            _i48_v58 = Set()
            _U_Q_ub[_i48_v57_key] = _i48_v58
        _U_Q_ub[_i48_v57_key].add(_i48_v57_value)
        # End inlined _maint__U_Q_ub_for__U_Q_add.
        # Begin inlined _maint_R_Q_T_group_for__U_Q_add.
        (_i49_elem,) = (_elem,)
        (_i49_v22_celeb, _i49_v22_group) = _i49_elem
        _i49_v22_result = (_i49_v22_group,)
        if (_i49_v22_result not in R_Q_T_group):
            R_Q_T_group.add(_i49_v22_result)
            # Begin inlined _maint_R_Q_d_M_2_for_R_Q_T_group_add.
            (_i49_i35_elem,) = (_i49_v22_result,)
            (_i49_i35_v36_group,) = _i49_i35_elem
            for _i49_i35_v36_user in _i49_i35_v36_group:
                _i49_i35_v36_result = (_i49_i35_v36_group, _i49_i35_v36_user)
                R_Q_d_M_2.add(_i49_i35_v36_result)
                # Begin inlined _maint_R_Q_T_user_2_for_R_Q_d_M_2_add.
                (_i49_i35_i29_elem,) = (_i49_i35_v36_result,)
                (_i49_i35_i29_v40_group, _i49_i35_i29_v40_user) = _i49_i35_i29_elem
                _i49_i35_i29_v40_result = (_i49_i35_i29_v40_user,)
                if (_i49_i35_i29_v40_result not in R_Q_T_user_2):
                    R_Q_T_user_2.add(_i49_i35_i29_v40_result)
                    # Begin inlined _maint_R_Q_d_F_email_for_R_Q_T_user_2_add.
                    (_i49_i35_i29_i5_elem,) = (_i49_i35_i29_v40_result,)
                    (_i49_i35_i29_i5_v50_user,) = _i49_i35_i29_i5_elem
                    if ((_i49_i35_i29_i5_v50_user,) in R_Q_T_user_1):
                        _i49_i35_i29_i5_v50_user_email = _i49_i35_i29_i5_v50_user.email
                        _i49_i35_i29_i5_v50_result = (_i49_i35_i29_i5_v50_user, _i49_i35_i29_i5_v50_user_email)
                        R_Q_d_F_email.add(_i49_i35_i29_i5_v50_result)
                    # End inlined _maint_R_Q_d_F_email_for_R_Q_T_user_2_add.
                    # Begin inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_2_add.
                    (_i49_i35_i29_i6_elem,) = (_i49_i35_i29_v40_result,)
                    (_i49_i35_i29_i6_v44_user,) = _i49_i35_i29_i6_elem
                    if ((_i49_i35_i29_i6_v44_user,) in R_Q_T_user_1):
                        _i49_i35_i29_i6_v44_user_loc = _i49_i35_i29_i6_v44_user.loc
                        _i49_i35_i29_i6_v44_result = (_i49_i35_i29_i6_v44_user, _i49_i35_i29_i6_v44_user_loc)
                        R_Q_d_F_loc.add(_i49_i35_i29_i6_v44_result)
                    # End inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_2_add.
                else:
                    R_Q_T_user_2.inccount(_i49_i35_i29_v40_result)
                # End inlined _maint_R_Q_T_user_2_for_R_Q_d_M_2_add.
            # End inlined _maint_R_Q_d_M_2_for_R_Q_T_group_add.
        else:
            R_Q_T_group.inccount(_i49_v22_result)
        # End inlined _maint_R_Q_T_group_for__U_Q_add.
        # Begin inlined _maint_R_Q_T_celeb_for__U_Q_add.
        (_i50_elem,) = (_elem,)
        (_i50_v20_celeb, _i50_v20_group) = _i50_elem
        _i50_v20_result = (_i50_v20_celeb,)
        if (_i50_v20_result not in R_Q_T_celeb):
            R_Q_T_celeb.add(_i50_v20_result)
            # Begin inlined _maint_R_Q_d_F_followers_for_R_Q_T_celeb_add.
            (_i50_i45_elem,) = (_i50_v20_result,)
            (_i50_i45_v24_celeb,) = _i50_i45_elem
            _i50_i45_v24_celeb_followers = _i50_i45_v24_celeb.followers
            _i50_i45_v24_result = (_i50_i45_v24_celeb, _i50_i45_v24_celeb_followers)
            R_Q_d_F_followers.add(_i50_i45_v24_result)
            # Begin inlined _maint_R_Q_d_F_followers_ub_for_R_Q_d_F_followers_add.
            (_i50_i45_i37_elem,) = (_i50_i45_v24_result,)
            (_i50_i45_i37_elem_v1, _i50_i45_i37_elem_v2) = _i50_i45_i37_elem
            _i50_i45_i37_v60_key = _i50_i45_i37_elem_v2
            _i50_i45_i37_v60_value = _i50_i45_i37_elem_v1
            if (_i50_i45_i37_v60_key not in R_Q_d_F_followers_ub):
                _i50_i45_i37_v61 = Set()
                R_Q_d_F_followers_ub[_i50_i45_i37_v60_key] = _i50_i45_i37_v61
            R_Q_d_F_followers_ub[_i50_i45_i37_v60_key].add(_i50_i45_i37_v60_value)
            # End inlined _maint_R_Q_d_F_followers_ub_for_R_Q_d_F_followers_add.
            # Begin inlined _maint_R_Q_T_celeb_followers_for_R_Q_d_F_followers_add.
            (_i50_i45_i38_elem,) = (_i50_i45_v24_result,)
            (_i50_i45_i38_v28_celeb, _i50_i45_i38_v28_celeb_followers) = _i50_i45_i38_elem
            _i50_i45_i38_v28_result = (_i50_i45_i38_v28_celeb_followers,)
            if (_i50_i45_i38_v28_result not in R_Q_T_celeb_followers):
                R_Q_T_celeb_followers.add(_i50_i45_i38_v28_result)
                # Begin inlined _maint_R_Q_d_M_1_for_R_Q_T_celeb_followers_add.
                (_i50_i45_i38_i33_elem,) = (_i50_i45_i38_v28_result,)
                (_i50_i45_i38_i33_v30_celeb_followers,) = _i50_i45_i38_i33_elem
                for _i50_i45_i38_i33_v30_user in _i50_i45_i38_i33_v30_celeb_followers:
                    _i50_i45_i38_i33_v30_result = (_i50_i45_i38_i33_v30_celeb_followers, _i50_i45_i38_i33_v30_user)
                    R_Q_d_M_1.add(_i50_i45_i38_i33_v30_result)
                    # Begin inlined _maint_R_Q_d_M_1_ub_for_R_Q_d_M_1_add.
                    (_i50_i45_i38_i33_i21_elem,) = (_i50_i45_i38_i33_v30_result,)
                    (_i50_i45_i38_i33_i21_elem_v1, _i50_i45_i38_i33_i21_elem_v2) = _i50_i45_i38_i33_i21_elem
                    _i50_i45_i38_i33_i21_v63_key = _i50_i45_i38_i33_i21_elem_v2
                    _i50_i45_i38_i33_i21_v63_value = _i50_i45_i38_i33_i21_elem_v1
                    if (_i50_i45_i38_i33_i21_v63_key not in R_Q_d_M_1_ub):
                        _i50_i45_i38_i33_i21_v64 = Set()
                        R_Q_d_M_1_ub[_i50_i45_i38_i33_i21_v63_key] = _i50_i45_i38_i33_i21_v64
                    R_Q_d_M_1_ub[_i50_i45_i38_i33_i21_v63_key].add(_i50_i45_i38_i33_i21_v63_value)
                    # End inlined _maint_R_Q_d_M_1_ub_for_R_Q_d_M_1_add.
                    # Begin inlined _maint_R_Q_T_user_1_for_R_Q_d_M_1_add.
                    (_i50_i45_i38_i33_i22_elem,) = (_i50_i45_i38_i33_v30_result,)
                    (_i50_i45_i38_i33_i22_v34_celeb_followers, _i50_i45_i38_i33_i22_v34_user) = _i50_i45_i38_i33_i22_elem
                    _i50_i45_i38_i33_i22_v34_result = (_i50_i45_i38_i33_i22_v34_user,)
                    if (_i50_i45_i38_i33_i22_v34_result not in R_Q_T_user_1):
                        R_Q_T_user_1.add(_i50_i45_i38_i33_i22_v34_result)
                        # Begin inlined _maint_R_Q_d_F_email_for_R_Q_T_user_1_add.
                        (_i50_i45_i38_i33_i22_i1_elem,) = (_i50_i45_i38_i33_i22_v34_result,)
                        (_i50_i45_i38_i33_i22_i1_v48_user,) = _i50_i45_i38_i33_i22_i1_elem
                        if ((_i50_i45_i38_i33_i22_i1_v48_user,) in R_Q_T_user_2):
                            _i50_i45_i38_i33_i22_i1_v48_user_email = _i50_i45_i38_i33_i22_i1_v48_user.email
                            _i50_i45_i38_i33_i22_i1_v48_result = (_i50_i45_i38_i33_i22_i1_v48_user, _i50_i45_i38_i33_i22_i1_v48_user_email)
                            R_Q_d_F_email.add(_i50_i45_i38_i33_i22_i1_v48_result)
                        # End inlined _maint_R_Q_d_F_email_for_R_Q_T_user_1_add.
                        # Begin inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_1_add.
                        (_i50_i45_i38_i33_i22_i2_elem,) = (_i50_i45_i38_i33_i22_v34_result,)
                        (_i50_i45_i38_i33_i22_i2_v42_user,) = _i50_i45_i38_i33_i22_i2_elem
                        if ((_i50_i45_i38_i33_i22_i2_v42_user,) in R_Q_T_user_2):
                            _i50_i45_i38_i33_i22_i2_v42_user_loc = _i50_i45_i38_i33_i22_i2_v42_user.loc
                            _i50_i45_i38_i33_i22_i2_v42_result = (_i50_i45_i38_i33_i22_i2_v42_user, _i50_i45_i38_i33_i22_i2_v42_user_loc)
                            R_Q_d_F_loc.add(_i50_i45_i38_i33_i22_i2_v42_result)
                        # End inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_1_add.
                    else:
                        R_Q_T_user_1.inccount(_i50_i45_i38_i33_i22_v34_result)
                    # End inlined _maint_R_Q_T_user_1_for_R_Q_d_M_1_add.
                # End inlined _maint_R_Q_d_M_1_for_R_Q_T_celeb_followers_add.
            else:
                R_Q_T_celeb_followers.inccount(_i50_i45_i38_v28_result)
            # End inlined _maint_R_Q_T_celeb_followers_for_R_Q_d_F_followers_add.
            # End inlined _maint_R_Q_d_F_followers_for_R_Q_T_celeb_add.
        else:
            R_Q_T_celeb.inccount(_i50_v20_result)
        # End inlined _maint_R_Q_T_celeb_for__U_Q_add.
        # Begin inlined _maint_R_Q_for__U_Q_add.
        (_i51_elem,) = (_elem,)
        (_i51_v10_celeb, _i51_v10_group) = _i51_elem
        if ((_i51_v10_celeb, _i51_v10_group) in _U_Q):
            _i51_v10_celeb_followers = _i51_v10_celeb.followers
            for _i51_v10_user in _i51_v10_celeb_followers:
                if (_i51_v10_user in _i51_v10_group):
                    _i51_v10_user_loc = _i51_v10_user.loc
                    if (_i51_v10_user_loc == 'NYC'):
                        _i51_v10_user_email = _i51_v10_user.email
                        _i51_v10_result = (_i51_v10_celeb, _i51_v10_group, _i51_v10_user_email)
                        # Begin inlined _maint_R_Q_bbu_for_R_Q_add.
                        (_i51_i9_elem,) = (_i51_v10_result,)
                        (_i51_i9_elem_v1, _i51_i9_elem_v2, _i51_i9_elem_v3) = _i51_i9_elem
                        _i51_i9_v66_key = (_i51_i9_elem_v1, _i51_i9_elem_v2)
                        _i51_i9_v66_value = _i51_i9_elem_v3
                        if (_i51_i9_v66_key not in R_Q_bbu):
                            _i51_i9_v67 = Set()
                            R_Q_bbu[_i51_i9_v66_key] = _i51_i9_v67
                        R_Q_bbu[_i51_i9_v66_key].add(_i51_i9_v66_value)
                        # End inlined _maint_R_Q_bbu_for_R_Q_add.
        # End inlined _maint_R_Q_for__U_Q_add.

def make_user(email, loc):
    ### Deleted code throughout this function.
    u = Obj()
    _v1 = (u, Set())
    index(_v1, 0).followers = index(_v1, 1)
    _v2 = (u, email)
    index(_v2, 0).email = index(_v2, 1)
    _v3 = (u, loc)
    index(_v3, 0).loc = index(_v3, 1)
    return u

def make_group():
    g = Set()
    return g

def follow(u, c):
    assert (u not in c.followers)
    _v4 = (c.followers, u)
    index(_v4, 0).add(index(_v4, 1))
    ### Deleted code.
    # Begin inlined _maint_R_Q_d_M_1_for__M_add.
    (_i59_elem,) = (_v4,)
    (_i59_v32_celeb_followers, _i59_v32_user) = _i59_elem
    if ((_i59_v32_celeb_followers,) in R_Q_T_celeb_followers):
        _i59_v32_result = (_i59_v32_celeb_followers, _i59_v32_user)
        R_Q_d_M_1.add(_i59_v32_result)
        # Begin inlined _maint_R_Q_d_M_1_ub_for_R_Q_d_M_1_add.
        (_i59_i23_elem,) = (_i59_v32_result,)
        (_i59_i23_elem_v1, _i59_i23_elem_v2) = _i59_i23_elem
        _i59_i23_v63_key = _i59_i23_elem_v2
        _i59_i23_v63_value = _i59_i23_elem_v1
        if (_i59_i23_v63_key not in R_Q_d_M_1_ub):
            _i59_i23_v64 = Set()
            R_Q_d_M_1_ub[_i59_i23_v63_key] = _i59_i23_v64
        R_Q_d_M_1_ub[_i59_i23_v63_key].add(_i59_i23_v63_value)
        # End inlined _maint_R_Q_d_M_1_ub_for_R_Q_d_M_1_add.
        # Begin inlined _maint_R_Q_T_user_1_for_R_Q_d_M_1_add.
        (_i59_i24_elem,) = (_i59_v32_result,)
        (_i59_i24_v34_celeb_followers, _i59_i24_v34_user) = _i59_i24_elem
        _i59_i24_v34_result = (_i59_i24_v34_user,)
        if (_i59_i24_v34_result not in R_Q_T_user_1):
            R_Q_T_user_1.add(_i59_i24_v34_result)
            # Begin inlined _maint_R_Q_d_F_email_for_R_Q_T_user_1_add.
            (_i59_i24_i1_elem,) = (_i59_i24_v34_result,)
            (_i59_i24_i1_v48_user,) = _i59_i24_i1_elem
            if ((_i59_i24_i1_v48_user,) in R_Q_T_user_2):
                _i59_i24_i1_v48_user_email = _i59_i24_i1_v48_user.email
                _i59_i24_i1_v48_result = (_i59_i24_i1_v48_user, _i59_i24_i1_v48_user_email)
                R_Q_d_F_email.add(_i59_i24_i1_v48_result)
            # End inlined _maint_R_Q_d_F_email_for_R_Q_T_user_1_add.
            # Begin inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_1_add.
            (_i59_i24_i2_elem,) = (_i59_i24_v34_result,)
            (_i59_i24_i2_v42_user,) = _i59_i24_i2_elem
            if ((_i59_i24_i2_v42_user,) in R_Q_T_user_2):
                _i59_i24_i2_v42_user_loc = _i59_i24_i2_v42_user.loc
                _i59_i24_i2_v42_result = (_i59_i24_i2_v42_user, _i59_i24_i2_v42_user_loc)
                R_Q_d_F_loc.add(_i59_i24_i2_v42_result)
            # End inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_1_add.
        else:
            R_Q_T_user_1.inccount(_i59_i24_v34_result)
        # End inlined _maint_R_Q_T_user_1_for_R_Q_d_M_1_add.
    # End inlined _maint_R_Q_d_M_1_for__M_add.
    # Begin inlined _maint_R_Q_for__M_add.
    (_i60_elem,) = (_v4,)
    (_i60_v14_celeb_followers, _i60_v14_user) = _i60_elem
    if ((_i60_v14_celeb_followers, _i60_v14_user) in R_Q_d_M_1):
        _i60_v14_user_loc = _i60_v14_user.loc
        if (_i60_v14_user_loc == 'NYC'):
            _i60_v14_user_email = _i60_v14_user.email
            for _i60_v14_celeb in R_Q_d_F_followers_ub.get(_i60_v14_celeb_followers, Set()):
                for _i60_v14_group in _U_Q_bu.get(_i60_v14_celeb, Set()):
                    if (_i60_v14_user in _i60_v14_group):
                        if ((_i60_v14_group, _i60_v14_user) != _i60_elem):
                            _i60_v14_result = (_i60_v14_celeb, _i60_v14_group, _i60_v14_user_email)
                            # Begin inlined _maint_R_Q_bbu_for_R_Q_add.
                            (_i60_i11_elem,) = (_i60_v14_result,)
                            (_i60_i11_elem_v1, _i60_i11_elem_v2, _i60_i11_elem_v3) = _i60_i11_elem
                            _i60_i11_v66_key = (_i60_i11_elem_v1, _i60_i11_elem_v2)
                            _i60_i11_v66_value = _i60_i11_elem_v3
                            if (_i60_i11_v66_key not in R_Q_bbu):
                                _i60_i11_v67 = Set()
                                R_Q_bbu[_i60_i11_v66_key] = _i60_i11_v67
                            R_Q_bbu[_i60_i11_v66_key].add(_i60_i11_v66_value)
                            # End inlined _maint_R_Q_bbu_for_R_Q_add.
    ### Deleted code.
    # End inlined _maint_R_Q_for__M_add.

def unfollow(u, c):
    assert (u in c.followers)
    _v5 = (c.followers, u)
    # Begin inlined _maint_R_Q_for__M_remove.
    (_i61_elem,) = (_v5,)
    (_i61_v15_celeb_followers, _i61_v15_user) = _i61_elem
    if ((_i61_v15_celeb_followers, _i61_v15_user) in R_Q_d_M_1):
        _i61_v15_user_loc = _i61_v15_user.loc
        if (_i61_v15_user_loc == 'NYC'):
            _i61_v15_user_email = _i61_v15_user.email
            for _i61_v15_celeb in R_Q_d_F_followers_ub.get(_i61_v15_celeb_followers, Set()):
                for _i61_v15_group in _U_Q_bu.get(_i61_v15_celeb, Set()):
                    if (_i61_v15_user in _i61_v15_group):
                        if ((_i61_v15_group, _i61_v15_user) != _i61_elem):
                            _i61_v15_result = (_i61_v15_celeb, _i61_v15_group, _i61_v15_user_email)
                            # Begin inlined _maint_R_Q_bbu_for_R_Q_remove.
                            (_i61_i17_elem,) = (_i61_v15_result,)
                            (_i61_i17_elem_v1, _i61_i17_elem_v2, _i61_i17_elem_v3) = _i61_i17_elem
                            _i61_i17_v68_key = (_i61_i17_elem_v1, _i61_i17_elem_v2)
                            _i61_i17_v68_value = _i61_i17_elem_v3
                            R_Q_bbu[_i61_i17_v68_key].remove(_i61_i17_v68_value)
                            if (len(R_Q_bbu[_i61_i17_v68_key]) == 0):
                                del R_Q_bbu[_i61_i17_v68_key]
                            # End inlined _maint_R_Q_bbu_for_R_Q_remove.
    ### Deleted code.
    # End inlined _maint_R_Q_for__M_remove.
    # Begin inlined _maint_R_Q_d_M_1_for__M_remove.
    (_i62_elem,) = (_v5,)
    (_i62_v33_celeb_followers, _i62_v33_user) = _i62_elem
    if ((_i62_v33_celeb_followers,) in R_Q_T_celeb_followers):
        _i62_v33_result = (_i62_v33_celeb_followers, _i62_v33_user)
        # Begin inlined _maint_R_Q_T_user_1_for_R_Q_d_M_1_remove.
        (_i62_i27_elem,) = (_i62_v33_result,)
        (_i62_i27_v35_celeb_followers, _i62_i27_v35_user) = _i62_i27_elem
        _i62_i27_v35_result = (_i62_i27_v35_user,)
        if (R_Q_T_user_1.getcount(_i62_i27_v35_result) == 1):
            # Begin inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_1_remove.
            (_i62_i27_i3_elem,) = (_i62_i27_v35_result,)
            (_i62_i27_i3_v43_user,) = _i62_i27_i3_elem
            if ((_i62_i27_i3_v43_user,) in R_Q_T_user_2):
                _i62_i27_i3_v43_user_loc = _i62_i27_i3_v43_user.loc
                _i62_i27_i3_v43_result = (_i62_i27_i3_v43_user, _i62_i27_i3_v43_user_loc)
                R_Q_d_F_loc.remove(_i62_i27_i3_v43_result)
            # End inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_1_remove.
            # Begin inlined _maint_R_Q_d_F_email_for_R_Q_T_user_1_remove.
            (_i62_i27_i4_elem,) = (_i62_i27_v35_result,)
            (_i62_i27_i4_v49_user,) = _i62_i27_i4_elem
            if ((_i62_i27_i4_v49_user,) in R_Q_T_user_2):
                _i62_i27_i4_v49_user_email = _i62_i27_i4_v49_user.email
                _i62_i27_i4_v49_result = (_i62_i27_i4_v49_user, _i62_i27_i4_v49_user_email)
                R_Q_d_F_email.remove(_i62_i27_i4_v49_result)
            # End inlined _maint_R_Q_d_F_email_for_R_Q_T_user_1_remove.
            R_Q_T_user_1.remove(_i62_i27_v35_result)
        else:
            R_Q_T_user_1.deccount(_i62_i27_v35_result)
        # End inlined _maint_R_Q_T_user_1_for_R_Q_d_M_1_remove.
        # Begin inlined _maint_R_Q_d_M_1_ub_for_R_Q_d_M_1_remove.
        (_i62_i28_elem,) = (_i62_v33_result,)
        (_i62_i28_elem_v1, _i62_i28_elem_v2) = _i62_i28_elem
        _i62_i28_v65_key = _i62_i28_elem_v2
        _i62_i28_v65_value = _i62_i28_elem_v1
        R_Q_d_M_1_ub[_i62_i28_v65_key].remove(_i62_i28_v65_value)
        if (len(R_Q_d_M_1_ub[_i62_i28_v65_key]) == 0):
            del R_Q_d_M_1_ub[_i62_i28_v65_key]
        # End inlined _maint_R_Q_d_M_1_ub_for_R_Q_d_M_1_remove.
        R_Q_d_M_1.remove(_i62_v33_result)
    # End inlined _maint_R_Q_d_M_1_for__M_remove.
    ### Deleted code.
    index(_v5, 0).remove(index(_v5, 1))

def join_group(u, g):
    assert (u not in g)
    _v6 = (g, u)
    index(_v6, 0).add(index(_v6, 1))
    # Begin inlined _maint_R_Q_d_M_2_for__M_add.
    (_i64_elem,) = (_v6,)
    (_i64_v38_group, _i64_v38_user) = _i64_elem
    if ((_i64_v38_group,) in R_Q_T_group):
        _i64_v38_result = (_i64_v38_group, _i64_v38_user)
        R_Q_d_M_2.add(_i64_v38_result)
        # Begin inlined _maint_R_Q_T_user_2_for_R_Q_d_M_2_add.
        (_i64_i30_elem,) = (_i64_v38_result,)
        (_i64_i30_v40_group, _i64_i30_v40_user) = _i64_i30_elem
        _i64_i30_v40_result = (_i64_i30_v40_user,)
        if (_i64_i30_v40_result not in R_Q_T_user_2):
            R_Q_T_user_2.add(_i64_i30_v40_result)
            # Begin inlined _maint_R_Q_d_F_email_for_R_Q_T_user_2_add.
            (_i64_i30_i5_elem,) = (_i64_i30_v40_result,)
            (_i64_i30_i5_v50_user,) = _i64_i30_i5_elem
            if ((_i64_i30_i5_v50_user,) in R_Q_T_user_1):
                _i64_i30_i5_v50_user_email = _i64_i30_i5_v50_user.email
                _i64_i30_i5_v50_result = (_i64_i30_i5_v50_user, _i64_i30_i5_v50_user_email)
                R_Q_d_F_email.add(_i64_i30_i5_v50_result)
            # End inlined _maint_R_Q_d_F_email_for_R_Q_T_user_2_add.
            # Begin inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_2_add.
            (_i64_i30_i6_elem,) = (_i64_i30_v40_result,)
            (_i64_i30_i6_v44_user,) = _i64_i30_i6_elem
            if ((_i64_i30_i6_v44_user,) in R_Q_T_user_1):
                _i64_i30_i6_v44_user_loc = _i64_i30_i6_v44_user.loc
                _i64_i30_i6_v44_result = (_i64_i30_i6_v44_user, _i64_i30_i6_v44_user_loc)
                R_Q_d_F_loc.add(_i64_i30_i6_v44_result)
            # End inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_2_add.
        else:
            R_Q_T_user_2.inccount(_i64_i30_v40_result)
        # End inlined _maint_R_Q_T_user_2_for_R_Q_d_M_2_add.
    # End inlined _maint_R_Q_d_M_2_for__M_add.
    ### Deleted code.
    # Begin inlined _maint_R_Q_for__M_add.
    (_i66_elem,) = (_v6,)
    ### Deleted code.
    (_i66_v14_group, _i66_v14_user) = _i66_elem
    if ((_i66_v14_group, _i66_v14_user) in R_Q_d_M_2):
        _i66_v14_user_loc = _i66_v14_user.loc
        if (_i66_v14_user_loc == 'NYC'):
            _i66_v14_user_email = _i66_v14_user.email
            for _i66_v14_celeb in _U_Q_ub.get(_i66_v14_group, Set()):
                _i66_v14_celeb_followers = _i66_v14_celeb.followers
                if (_i66_v14_user in _i66_v14_celeb_followers):
                    _i66_v14_result = (_i66_v14_celeb, _i66_v14_group, _i66_v14_user_email)
                    # Begin inlined _maint_R_Q_bbu_for_R_Q_add.
                    (_i66_i12_elem,) = (_i66_v14_result,)
                    (_i66_i12_elem_v1, _i66_i12_elem_v2, _i66_i12_elem_v3) = _i66_i12_elem
                    _i66_i12_v66_key = (_i66_i12_elem_v1, _i66_i12_elem_v2)
                    _i66_i12_v66_value = _i66_i12_elem_v3
                    if (_i66_i12_v66_key not in R_Q_bbu):
                        _i66_i12_v67 = Set()
                        R_Q_bbu[_i66_i12_v66_key] = _i66_i12_v67
                    R_Q_bbu[_i66_i12_v66_key].add(_i66_i12_v66_value)
                    # End inlined _maint_R_Q_bbu_for_R_Q_add.
    # End inlined _maint_R_Q_for__M_add.

def leave_group(u, g):
    assert (u in g)
    _v7 = (g, u)
    # Begin inlined _maint_R_Q_for__M_remove.
    (_i67_elem,) = (_v7,)
    ### Deleted code.
    (_i67_v15_group, _i67_v15_user) = _i67_elem
    if ((_i67_v15_group, _i67_v15_user) in R_Q_d_M_2):
        _i67_v15_user_loc = _i67_v15_user.loc
        if (_i67_v15_user_loc == 'NYC'):
            _i67_v15_user_email = _i67_v15_user.email
            for _i67_v15_celeb in _U_Q_ub.get(_i67_v15_group, Set()):
                _i67_v15_celeb_followers = _i67_v15_celeb.followers
                if (_i67_v15_user in _i67_v15_celeb_followers):
                    _i67_v15_result = (_i67_v15_celeb, _i67_v15_group, _i67_v15_user_email)
                    # Begin inlined _maint_R_Q_bbu_for_R_Q_remove.
                    (_i67_i18_elem,) = (_i67_v15_result,)
                    (_i67_i18_elem_v1, _i67_i18_elem_v2, _i67_i18_elem_v3) = _i67_i18_elem
                    _i67_i18_v68_key = (_i67_i18_elem_v1, _i67_i18_elem_v2)
                    _i67_i18_v68_value = _i67_i18_elem_v3
                    R_Q_bbu[_i67_i18_v68_key].remove(_i67_i18_v68_value)
                    if (len(R_Q_bbu[_i67_i18_v68_key]) == 0):
                        del R_Q_bbu[_i67_i18_v68_key]
                    # End inlined _maint_R_Q_bbu_for_R_Q_remove.
    # End inlined _maint_R_Q_for__M_remove.
    ### Deleted code.
    # Begin inlined _maint_R_Q_d_M_2_for__M_remove.
    (_i69_elem,) = (_v7,)
    (_i69_v39_group, _i69_v39_user) = _i69_elem
    if ((_i69_v39_group,) in R_Q_T_group):
        _i69_v39_result = (_i69_v39_group, _i69_v39_user)
        # Begin inlined _maint_R_Q_T_user_2_for_R_Q_d_M_2_remove.
        (_i69_i32_elem,) = (_i69_v39_result,)
        (_i69_i32_v41_group, _i69_i32_v41_user) = _i69_i32_elem
        _i69_i32_v41_result = (_i69_i32_v41_user,)
        if (R_Q_T_user_2.getcount(_i69_i32_v41_result) == 1):
            # Begin inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_2_remove.
            (_i69_i32_i7_elem,) = (_i69_i32_v41_result,)
            (_i69_i32_i7_v45_user,) = _i69_i32_i7_elem
            if ((_i69_i32_i7_v45_user,) in R_Q_T_user_1):
                _i69_i32_i7_v45_user_loc = _i69_i32_i7_v45_user.loc
                _i69_i32_i7_v45_result = (_i69_i32_i7_v45_user, _i69_i32_i7_v45_user_loc)
                R_Q_d_F_loc.remove(_i69_i32_i7_v45_result)
            # End inlined _maint_R_Q_d_F_loc_for_R_Q_T_user_2_remove.
            # Begin inlined _maint_R_Q_d_F_email_for_R_Q_T_user_2_remove.
            (_i69_i32_i8_elem,) = (_i69_i32_v41_result,)
            (_i69_i32_i8_v51_user,) = _i69_i32_i8_elem
            if ((_i69_i32_i8_v51_user,) in R_Q_T_user_1):
                _i69_i32_i8_v51_user_email = _i69_i32_i8_v51_user.email
                _i69_i32_i8_v51_result = (_i69_i32_i8_v51_user, _i69_i32_i8_v51_user_email)
                R_Q_d_F_email.remove(_i69_i32_i8_v51_result)
            # End inlined _maint_R_Q_d_F_email_for_R_Q_T_user_2_remove.
            R_Q_T_user_2.remove(_i69_i32_v41_result)
        else:
            R_Q_T_user_2.deccount(_i69_i32_v41_result)
        # End inlined _maint_R_Q_T_user_2_for_R_Q_d_M_2_remove.
        R_Q_d_M_2.remove(_i69_v39_result)
    # End inlined _maint_R_Q_d_M_2_for__M_remove.
    index(_v7, 0).remove(index(_v7, 1))

def change_loc(u, loc):
    _v8 = (u, u.loc)
    # Begin inlined _maint_R_Q_for__F_loc_remove.
    (_i70_elem,) = (_v8,)
    (_i70_v17_user, _i70_v17_user_loc) = _i70_elem
    if ((_i70_v17_user, _i70_v17_user_loc) in R_Q_d_F_loc):
        if (_i70_v17_user_loc == 'NYC'):
            _i70_v17_user_email = _i70_v17_user.email
            for _i70_v17_celeb_followers in R_Q_d_M_1_ub.get(_i70_v17_user, Set()):
                for _i70_v17_celeb in R_Q_d_F_followers_ub.get(_i70_v17_celeb_followers, Set()):
                    for _i70_v17_group in _U_Q_bu.get(_i70_v17_celeb, Set()):
                        if (_i70_v17_user in _i70_v17_group):
                            _i70_v17_result = (_i70_v17_celeb, _i70_v17_group, _i70_v17_user_email)
                            # Begin inlined _maint_R_Q_bbu_for_R_Q_remove.
                            (_i70_i19_elem,) = (_i70_v17_result,)
                            (_i70_i19_elem_v1, _i70_i19_elem_v2, _i70_i19_elem_v3) = _i70_i19_elem
                            _i70_i19_v68_key = (_i70_i19_elem_v1, _i70_i19_elem_v2)
                            _i70_i19_v68_value = _i70_i19_elem_v3
                            R_Q_bbu[_i70_i19_v68_key].remove(_i70_i19_v68_value)
                            if (len(R_Q_bbu[_i70_i19_v68_key]) == 0):
                                del R_Q_bbu[_i70_i19_v68_key]
                            # End inlined _maint_R_Q_bbu_for_R_Q_remove.
    # End inlined _maint_R_Q_for__F_loc_remove.
    # Begin inlined _maint_R_Q_d_F_loc_for__F_loc_remove.
    (_i71_elem,) = (_v8,)
    (_i71_v47_user, _i71_v47_user_loc) = _i71_elem
    if ((_i71_v47_user,) in R_Q_T_user_1):
        if ((_i71_v47_user,) in R_Q_T_user_2):
            _i71_v47_result = (_i71_v47_user, _i71_v47_user_loc)
            R_Q_d_F_loc.remove(_i71_v47_result)
    # End inlined _maint_R_Q_d_F_loc_for__F_loc_remove.
    del index(_v8, 0).loc
    _v9 = (u, loc)
    index(_v9, 0).loc = index(_v9, 1)
    # Begin inlined _maint_R_Q_d_F_loc_for__F_loc_add.
    (_i72_elem,) = (_v9,)
    (_i72_v46_user, _i72_v46_user_loc) = _i72_elem
    if ((_i72_v46_user,) in R_Q_T_user_1):
        if ((_i72_v46_user,) in R_Q_T_user_2):
            _i72_v46_result = (_i72_v46_user, _i72_v46_user_loc)
            R_Q_d_F_loc.add(_i72_v46_result)
    # End inlined _maint_R_Q_d_F_loc_for__F_loc_add.
    # Begin inlined _maint_R_Q_for__F_loc_add.
    (_i73_elem,) = (_v9,)
    (_i73_v16_user, _i73_v16_user_loc) = _i73_elem
    if ((_i73_v16_user, _i73_v16_user_loc) in R_Q_d_F_loc):
        if (_i73_v16_user_loc == 'NYC'):
            _i73_v16_user_email = _i73_v16_user.email
            for _i73_v16_celeb_followers in R_Q_d_M_1_ub.get(_i73_v16_user, Set()):
                for _i73_v16_celeb in R_Q_d_F_followers_ub.get(_i73_v16_celeb_followers, Set()):
                    for _i73_v16_group in _U_Q_bu.get(_i73_v16_celeb, Set()):
                        if (_i73_v16_user in _i73_v16_group):
                            _i73_v16_result = (_i73_v16_celeb, _i73_v16_group, _i73_v16_user_email)
                            # Begin inlined _maint_R_Q_bbu_for_R_Q_add.
                            (_i73_i13_elem,) = (_i73_v16_result,)
                            (_i73_i13_elem_v1, _i73_i13_elem_v2, _i73_i13_elem_v3) = _i73_i13_elem
                            _i73_i13_v66_key = (_i73_i13_elem_v1, _i73_i13_elem_v2)
                            _i73_i13_v66_value = _i73_i13_elem_v3
                            if (_i73_i13_v66_key not in R_Q_bbu):
                                _i73_i13_v67 = Set()
                                R_Q_bbu[_i73_i13_v66_key] = _i73_i13_v67
                            R_Q_bbu[_i73_i13_v66_key].add(_i73_i13_v66_value)
                            # End inlined _maint_R_Q_bbu_for_R_Q_add.
    # End inlined _maint_R_Q_for__F_loc_add.

def do_query(celeb, group):
    return ((_demand_Q((celeb, group)) or True) and R_Q_bbu.get((celeb, group), Set()))

def do_query_nodemand(celeb, group):
    return R_Q_bbu.get((celeb, group), Set())

