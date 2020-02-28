from django.template.defaultfilters import register
from django.template.defaultfilters import floatformat

@register.filter(name='lookup')
def lookup(dict, index):
    if index in dict:
        return dict[index]
    return ''

@register.filter(name='get_half1')
def get_half1(qset, user_id):
    try:
        half1 = qset.filter(id=user_id).values('half1')[0].get('half1')
    except:
        half1 = ""
    return half1

@register.filter(name='get_half2')
def get_half2(qset, user_id):
    try:
        half2 = qset.filter(id=user_id).values('half2')[0].get('half2')
    except:
        half2 = ""
    return half2

@register.filter(name='get_all')
def get_half1(qset, user_id):
    try:
        all = qset.filter(id=user_id).values('all')[0].get('all')
    except:
        all = ""
    return all

@register.filter(name='get_perc1')
def get_half1(qset, user_id):
    try:
        perc1 = floatformat(qset.filter(id=user_id).values('perc1')[0].get('perc1'),1)
    except:
        perc1 = ""
    return perc1

@register.filter(name='get_perc2')
def get_half1(qset, user_id):
    try:
        perc2 = floatformat(qset.filter(id=user_id).values('perc2')[0].get('perc2'),1)
    except:
        perc2 = ""
    return perc2

@register.filter(name='get_pall')
def get_all(qset, user_id):
    try:
        pall = floatformat(qset.filter(id=user_id).values('pall')[0].get('pall'),1)
    except:
        pall = ""
    return pall

@register.filter(name='win_half1')
def win_half1(dict, user):
    users =  dict['half1']
    if user in users:
        return user
    else:
        return ''

@register.filter(name='win_half2')
def win_half1(dict, user):
    users =  dict['half2']
    if user in users:
        return user
    else:
        return ''

@register.filter(name='get_winners')
def get_winners(qset, pick):
    week = qset.filter(week_no=pick.wk.week_no)
    if week.count() > 0:
        winners = week[0].week_winner()
    else:
        return ''
    return winners