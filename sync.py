#!/usr/bin/python3

import ldap,sys,os,time
pathtozmprov = "/opt/zimbra/bin/zmprov"


sysCallLenght = 20

ADbaseDN = "dc=site,dc=local"
ADdomain = "site.local"
ADauthDN = "CN=ZimbraLDAP,CN=Users,"+ADbaseDN
ADauthPass= "********"
ADfilter = "(&(objectClass=user)(objectClass=person)(memberOf=CN=email,OU=Access groups,"+ADbaseDN+")(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
ADAliasFeild = "mail"

ZimbraLdapServer = "ldap://zimbra-ldap-01.local"
ZimbraAuthDN = "uid=zimbra,cn=admins,cn=zimbra"
ZimbraAuthPass = "*******"
ZimbraUserFilter = "(&(objectClass=zimbraAccount)(objectClass=inetOrgPerson)(!(zimbraIsSystemAccount=*))(!(zimbraIsAdminAccount=*)))"


def split(arr, size):
     arrs = []
     while len(arr) > size:
         pice = arr[:size]
         arrs.append(pice)
         arr   = arr[size:]
     arrs.append(arr)
     return arrs

def getDataFromZimbra():
    ZimbraUsers = {}
    try:
        c = ldap.initialize(ZimbraLdapServer)
        c.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        c.set_option(ldap.OPT_REFERRALS, 0)
        c.simple_bind_s(ZimbraAuthDN,ZimbraAuthPass)
        result = c.search_s(ADbaseDN, ldap.SCOPE_SUBTREE,ZimbraUserFilter)
        for (dn, attr) in result:
            uid = attr['uid'][0].decode('UTF-8')
            uAttr = {}
            uAttr['status'] = False
            if 'zimbraMailAlias' in attr:
                aliases = []
                for (alias)  in attr['zimbraMailAlias']:
                    aliases.append(alias.decode('UTF-8'))
                uAttr['aliases'] = aliases
            ZimbraUsers[uid] = uAttr
        return ZimbraUsers
            

    except ldap.LDAPError as error_message:
        print ("ERROR: ",error_message)
        c.unbind_s()



ZimbraUsers = getDataFromZimbra()


try:
    c = ldap.initialize("ldap://"+ADdomain)
    c.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    c.set_option(ldap.OPT_REFERRALS, 0)
    c.simple_bind_s(ADauthDN,ADauthPass)

    result = c.search_s(ADbaseDN, ldap.SCOPE_SUBTREE,ADfilter)
    
    syscalls = []
    for (dn, vals) in result:
        try:
            accountname = vals['sAMAccountName'][0].lower().decode('UTF-8')
        except:
            continue
        try:
            aliases = vals[ADAliasFeild][0].decode('UTF-8').split(',')
            aliases = ['%s@%s' % (i.strip(),ADdomain) for i in aliases]
        except:
            aliases = []
        password = "  \'\' "

        sys.stdout.flush()
        email= '%s@%s' % (accountname,ADdomain)

        if accountname  not in ZimbraUsers:  
            syscalls.append('ca %s %s' % (email,password))
            if len(aliases) > 0 :
                for (alias) in aliases:
                    syscalls.append('aaa %s %s' % (email,alias))
        else:
            ZimbraUsers[accountname]['status'] = True
            if (len(aliases) > 0) and ('aliases' not in ZimbraUsers[accountname]):
                for (alias) in aliases:
                    syscalls.append('aaa %s %s' % (email,alias))
            elif (len(aliases) == 0) and ('aliases' in ZimbraUsers[accountname]):
                for (alias) in ZimbraUsers[accountname]['aliases']:
                    syscalls.append('raa %s %s' % (email,alias))
            else:
                addAlias = list(set(ZimbraUsers[accountname]['aliases']) - set(aliases))
                removeAlias = list(set(aliases) - set(ZimbraUsers[accountname]['aliases']))
                for (alias) in addAlias:
                    syscalls.append('aaa %s %s' % (email,alias))
                for (alias) in removeAlias:
                    syscalls.append('raa %s %s' % (email,alias))
    #Разделение комманд на группы
    if len(syscalls) > 0:
        while len(syscalls) > sysCallLenght:
             pice = syscalls[:sysCallLenght]
             os.system('echo "%s" | %s' % ('\n'.join(pice),pathtozmprov))
             syscalls   = syscalls[sysCallLenght:]
        os.system('echo "%s" | %s' % ('\n'.join(syscalls),pathtozmprov))
   
except ldap.LDAPError as error_message:
    print ("ERROR: ",error_message)
    c.unbind_s()
