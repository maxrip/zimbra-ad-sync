## This project is designed for one-way synchronization of users from ldap or ad.
It solves the following problems:
  - creating new users
  - optional blocking of users who were not found during subsequent synchronizations
  - synchronization of attributes from the domain (the ability to specify a combination of attributes of the mail ldap and the source ldap)
  - synchronization of mail aliases
  - DL synchronization based on domain groups (DL and group must have the same name)

## First step
`` cp config.yml.sample config.yml `` and edit section **remote** - freeipda or MS AD, **local** - carbonio or zimbra
 - basedn
 - authdn
 - authpassword
 - filter
 - dlfilter

**remote.filter** - in sample config working in freeipa for user located in group **email-user** and enabled status

**dlfilter** - in sample config working in freeipa group, located OU email-dl. 

For this block to work, you must first create a DL in carbonio with the ``same name`` as the group in ldap

**aliasAttribute** - work in format ``smtp:alias@site.com`` in gui freeipa, not tested in MS AD

## Enable authorization in Carbonio or Zimbra via external ldap
```
su - zextras

carbonio prov modifyDomain site.com zimbraAuthFallbackToLocal TRUE
carbonio prov modifyDomain site.com zimbraAuthLdapBindDn "uid=%u,cn=users,cn=accounts,dc=site,dc=com"
carbonio prov modifyDomain site.com zimbraAuthLdapSearchBase "cn=users,cn=accounts,dc=site,dc=com"
carbonio prov modifyDomain site.com zimbraAuthLdapStartTlsEnabled TRUE
carbonio prov modifyDomain site.com zimbraAuthLdapURL "ldaps://dc1.site.com"
carbonio prov modifyDomain site.com zimbraAutoProvAuthMech  LDAP
```
