import ldap

class LocalLdap:
    connect = None
    logger = None
    config = None
    local = None
    
    def __init__(self,logger,config):
        self.logger=logger
        self.config=config
        self.local=config['local']
        self.site=config['site']
    
    def getLdapConnect(self):
        if self.connect is None:
            c = ldap.initialize(self.local['url'])
            c.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            c.set_option(ldap.OPT_REFERRALS, 0)
            self.connect = c
        return self.connect
    
    def sync(self):
        self.getUsersFromCarbonio()
        self.getDlFromCarbonio()
        
    def getUsersFromCarbonio(self):
        LocalUsers = {}
        try:
            c = self.getLdapConnect()
            c.simple_bind_s(self.local['authdn'],self.local['authpassword'])
            result = c.search_s(self.local['basedn'], ldap.SCOPE_SUBTREE,self.local['filter'])
            for (dn, attr) in result:
                uid = attr['uid'][0].decode('UTF-8')
                uAttr = {}
                uAttr['email'] = '%s@%s' % (uid,self.site)

                if attr['zimbraAccountStatus'][0].decode('UTF-8') == 'active':
                    uAttr['status'] = True
                else:
                    uAttr['status'] = False

                if 'zimbraMailAlias' in attr:
                    aliases = []
                    for (alias)  in attr['zimbraMailAlias']:
                        aliases.append(alias.decode('UTF-8'))
                    uAttr['aliases'] = aliases
                else:
                    uAttr['aliases'] = []
                uAttr['attr'] = {}
                for key in self.local['attrmapper']:
                    try:
                        uAttr['attr'][key] = attr[key][0].decode('UTF-8')
                    except:
                        continue
                LocalUsers[uid] = uAttr
            self.users=LocalUsers
            self.logger.debug('get local users: %s',self.users)
        except ldap.LDAPError as error_message:
            logger.error("local: %s",error_message)
            c.unbind_s()
            raise error_message
        
            
    def getDlFromCarbonio(self):
        DL = {}
        try:
            c = self.getLdapConnect()
            c.simple_bind_s(self.local['authdn'],self.local['authpassword'])
            
            result = c.search_s(self.local['basedn'], ldap.SCOPE_SUBTREE,self.local['dlfilter'])
            
            for (dn, attr) in result:
                uid = attr['cn'][0].decode('UTF-8')
                zimbraId = attr['zimbraId'][0].decode('UTF-8')
                
                members = []
                for member in attr['zimbraMailForwardingAddress']:
                    members.append(member.decode('UTF-8'))
                    
                DL[uid] = {'members': members,'zimbraId':zimbraId}
            self.dl=DL
            self.logger.debug('get local dl: %s',self.dl)
            
        except ldap.LDAPError as error_message:
            logger.error("local: %s",error_message)
            c.unbind_s()
            raise error_message