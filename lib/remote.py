import ldap

class RemoteLdap:
    connect = None
    logger = None
    config = None
    remote = None
    local = None
    
    def __init__(self,logger,config):
        self.logger=logger
        self.config=config
        self.remote=config['remote']
        self.local=config['local']
        self.site=config['site']
    
    def getLdapConnect(self):
        if self.connect is None:
            c = ldap.initialize(self.remote['url'])
            c.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            c.set_option(ldap.OPT_REFERRALS, 0)
            self.connect = c
        return self.connect
    
    def sync(self):
        self.getUsersFromLdap()
        self.getDlFromLdap()
        
    def getUsersFromLdap(self):
        Users = {}
        try:
            c = self.getLdapConnect()
            c.simple_bind_s(self.remote['authdn'],self.remote['authpassword'])
            result = c.search_s(self.remote['basedn'], ldap.SCOPE_SUBTREE,self.remote['filter'])
            for (dn, attr) in result:
                uid = attr[self.remote['sn']][0].decode('UTF-8')
                uAttr = {}
                uAttr['email'] = '%s@%s' % (uid,self.site)
#                uAttr['status'] = False
                try:
                    if (len(self.remote['aliasAttribute']) > 0):
                        aliases = []
                        for aliase in attr[self.remote['aliasAttribute']]:
                            _alias = aliase.decode('UTF-8').lower().split(':')[1]
                            if _alias !=  uAttr['email']:
                                aliases.append(_alias)
                    else:
                        aliases = []
                except Exception as err:
                    aliases = []
                uAttr['aliases'] = aliases
                
                uAttr['attr'] = {}
                for key in self.local['attrmapper']:
                    try:
                        uAttr['attr'][key] = attr[self.remote['attrmapper'][key]][0].decode('UTF-8')
                    except Exception as err:
                        continue
                
                Users[uid] = uAttr
            self.users=Users
            self.logger.debug('get remote users: %s',self.users)
        except ldap.LDAPError as error_message:
            logger.error("remote: %s",error_message)
            c.unbind_s()
            raise error_message
        
            
    def getDlFromLdap(self):
        DL = {}
        try:
            c = self.getLdapConnect()
            c.simple_bind_s(self.remote['authdn'],self.remote['authpassword'])
            
            result = c.search_s(self.remote['basedn'], ldap.SCOPE_SUBTREE,self.remote['dlfilter'])
            
            for (dn, attr) in result:
                uid = attr['cn'][0].decode('UTF-8')
                members = []
                for member in attr[self.remote['dlfilter-attr']]:
                    members.append("%s@%s" % (member.decode('UTF-8').split(',')[0].split('=')[1],self.site))

                DL[uid] = {'members': members}
            self.dl=DL
            self.logger.debug('get remote dl: %s',self.dl)
            
        except ldap.LDAPError as error_message:
            logger.error("remote: %s",error_message)
            c.unbind_s()
            raise error_message