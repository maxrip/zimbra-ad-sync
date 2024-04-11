import os

class Cli:
    password = "  \'\' "
    #pathtozmprov = '/opt/zextras/bin/carbonio prov'
    pathtozmprov = '/opt/zextras/bin/zmprov'
    
    def addNewAccount(user):
        _localAttr = " ".join("'{}' '{}'".format(k, v) for k, v in user['attr'].items())
        return "ca %s %s %s" % (user['email'],Cli.password,_localAttr)


    def modifyAccount(user,attr):
        _localAttr = " ".join("'{}' '{}'".format(k, v) for k, v in attr.items())
        return "ma %s %s" % (user['email'],_localAttr)


    def addAlias(user,alias):
        return "aaa %s %s" % (user['email'],alias)
    
    
    def delAlias(user,alias):
        return "raa %s %s" % (user['email'],alias)
    
    
    def disabledAccount(user):
        return "ma %s zimbraAccountStatus locked" % (user['email'])
        
        
    def addDistributionListMember(user,dl):
        return "adlm %s %s" % (dl,user)
     
     
    def removeDistributionListMember(user,dl):
        return "rdlm %s %s" % (dl,user)


    def executeCarbonio(syscalls,sysCallLenght):
        for cmd in  syscalls:
            os.system("%s %s" %(Cli.pathtozmprov,cmd))
#        while len(syscalls) > sysCallLenght:
#            pice = syscalls[:sysCallLenght]
#            print('echo "%s" | %s' % ('\n'.join(pice),Cli.pathtozmprov))
#            os.system('echo "%s" | %s' % ('\n'.join(pice),Cli.pathtozmprov))
#            syscalls   = syscalls[sysCallLenght:]
#        print('echo "%s" | %s' % ('\n'.join(syscalls),Cli.pathtozmprov))
#        os.system('echo "%s" | %s' % ('\n'.join(syscalls),Cli.pathtozmprov))