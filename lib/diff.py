from lib.prov import Cli

class Diff:
    LocalUser = None
    RemoteUser = None
    LocalDl = None
    RemoteDl = None
    localAttr= None
    syscalls = []
    ignoringAccount = None
    
    def __init__(self,logger,config,LocalUser,RemoteUser,LocalDl,RemoteDl):
        self.logger = logger
        self.LocalUser = LocalUser
        self.RemoteUser = RemoteUser
        self.LocalDl = LocalDl
        self.RemoteDl = RemoteDl
        self.localAttr = config['local']['attrmapper']
        self.ignoringAccount = config['local']['ignoringAccount']

        if 'disabledNotFoundUser' in config['local'] and config['local']['disabledNotFoundUser'] == True:
            self.disabledNotFoundUser = True
        else:
            self.disabledNotFoundUser = False
        
        
    def generateUserDiff(self):
        #newUsers
        newUsers = set(self.RemoteUser) - set(self.LocalUser)
        self.logger.info('new users: %s',newUsers)
        if len(newUsers) > 0:
            for user in newUsers:
                self.syscalls.append(Cli.addNewAccount(self.RemoteUser[user]))
                if 'aliases' in self.RemoteUser[user] and len(self.RemoteUser[user]['aliases']) > 0:
                    self.logger.debug('%s found alias count: %s',user,len(self.RemoteUser[user]['aliases']))
                    for alias in self.RemoteUser[user]['aliases']:
                        self.syscalls.append(Cli.addAlias(self.RemoteUser[user],alias))
                    
        #oldUsers
        oldUsers =  set(self.LocalUser) & set(self.RemoteUser)
        self.logger.info('found local users: %s',oldUsers)
        if len(oldUsers) > 0:
            for user in oldUsers:
                _changedAttr = {}
                for key in self.localAttr:
                    if key not in self.LocalUser[user]['attr'] and key not in self.RemoteUser[user]['attr']:
                        continue
                    if key not in self.LocalUser[user]['attr'] and key in self.RemoteUser[user]['attr']:
                        _changedAttr[key] = self.RemoteUser[user]['attr'][key]
                        continue
                    if key in self.LocalUser[user]['attr'] and key not in self.RemoteUser[user]['attr']:
                       _changedAttr[key] = ''
                       continue
                    if self.LocalUser[user]['attr'][key] != self.RemoteUser[user]['attr'][key] :
                       _changedAttr[key] = self.RemoteUser[user]['attr'][key]
                if len(_changedAttr) > 0 :
                    self.logger.debug('update attr %s',_changedAttr)
                    self.syscalls.append(Cli.modifyAccount(self.RemoteUser[user],_changedAttr))
                
                self.__generateAliasDiff(user)
                
        #notFoundUsers
        notFoundUsers = set(self.LocalUser) - set(self.RemoteUser)
        self.logger.info('nof found users: %s',notFoundUsers)
        if len(oldUsers)> 0 and self.disabledNotFoundUser:
            for user in notFoundUsers:
                if self.LocalUser[user]['status'] and user not in self.ignoringAccount :
                    self.syscalls.append(Cli.disabledAccount(self.LocalUser[user]))

    def __generateAliasDiff(self,user):
        newAlises = set(self.RemoteUser[user]['aliases']) - set(self.LocalUser[user]['aliases'])
        if len(newAlises) > 0:
            self.logger.debug('new %s aliases: %s',self.RemoteUser[user]['email'],newAlises)
            for alias in newAlises:
                self.syscalls.append(Cli.addAlias(self.RemoteUser[user],alias))
        
        oldAlias = set(self.LocalUser[user]['aliases']) - set(self.RemoteUser[user]['aliases'])
        if len(oldAlias) > 0:
            self.logger.debug('remove %s aliases: %s',self.RemoteUser[user]['email'],oldAlias)
            for alias in oldAlias:
                self.syscalls.append(Cli.delAlias(self.RemoteUser[user],alias))
            
        
    def generateDlDiff(self):
        #not create DL in carbonio|zimbra. Only update members in DL
        if len(self.LocalDl) > 0:
            for dl in self.LocalDl:
                if dl in self.RemoteDl:
                    newUsers = set(self.RemoteDl[dl]['members']) - set(self.LocalDl[dl]['members'])
                    if len(newUsers) > 0:
                        self.logger.info('dl %s, new users: %s',dl,newUsers)
                        for user in newUsers:
                            self.syscalls.append(Cli.addDistributionListMember(user,self.LocalDl[dl]['zimbraId']))
                    
                    oldUsers = set(self.LocalDl[dl]['members']) - set(self.RemoteDl[dl]['members'])
                    if len(oldUsers) > 0:
                        self.logger.info('dl %s, remove users: %s',dl,oldUsers)
                        for user in oldUsers:
                            self.syscalls.append(Cli.removeDistributionListMember(user,self.LocalDl[dl]['zimbraId']))
                    