%include	/usr/lib/rpm/macros.python
Summary:	Simple virtualizing POP3 password interface
Summary(pl):	Prosty interfejs wirtualizuj±cy do POP3
Name:		vmailmgr
Version:	0.96.9
Release:	4
License:	GPL
Group:		Applications/System
Source0:	http://em.ca/~bruceg/vmailmgr/archive/%{version}/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}-qpop.inetd
Source3:	http://mricon.com/SM/guide/qvcs-guide.html
URL:		http://em.ca/~bruceg/vmailmgr/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	python-devel >= 2.2.1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	checkvpw

%define python_sitepkgsdir %(echo `python -c "import sys; print (sys.prefix + '/lib/python' + sys.version[:3] + '/site-packages/')"`)
%define python_compile_opt python -O -c "import compileall; compileall.compile_dir('.')"
%define python_compile python -c "import compileall; compileall.compile_dir('.')"

%description
Vmailmgr provides a virtualizing password-checking interface to
qmail-pop3d as well as both a delivery agent to automatically delivery
mail within a virtual domain and a set of tools to manage such a
domain.

%description -l pl
Vmailmgr dostarcza wirtualizuj±cy interfejs sprawdzaj±cy has³a do
qmail-pop3d oraz program dostarczaj±cy pocztê w domenie wirtualnej i
zestaw narzêdzi do obs³ugi takiej domeny.

%package cgi
Summary:	CGI applications for vmailmgr
Summary(pl):	Aplikacje CGI do vmailmgr
Group:		Applications/System
Requires:	vmailmgr-daemon = %{version}
Requires:	webserver

%description cgi
This package contains CGI applications to allow web-based
administration of vmailmgr systems.

%description cgi -l pl
Ten pakiet zawiera aplikacje CGI pozwalaj±ce na administracjê us³ugami
vmailmgr przez WWW.

%package php
Summary:	PHP applications for vmailmgr
Summary(pl):	Aplikacje PHP do vmailmgr
Group:		Applications/System
Requires:	vmailmgr-daemon = %{version}
Requires:	webserver

%description php
This package contains PHP applications to allow web-based
administration of vmailmgr systems.

%description php -l pl
Ten pakiet zawiera aplikacje PHP pozwalaj±ce na administracjê us³ugami
vmailmgr przez WWW.

%package daemon
Summary:	Vmailmgr daemon for CGIs
Summary(pl):	Demon vmailmgr dla CGI
Group:		Applications/System
PreReq:		rc-scripts
PreReq:		/sbin/chkconfig

%description daemon
This package contains the vmailmgrd daemon that provides virtual
domain manipulation services to support unprivileged clients like
CGIs.

%description daemon -l pl
Ten pakiet zawiera demona vmailmgrd pozwalaj±cego na manipulacjê
domenami wirtualnymi nieuprzywilejowanym klientom, takim jak CGI.

%package python
Summary:	Python modules and CGIs for vmailmgr
Summary(pl):	Modu³y pythona i CGI do vmailmgr
Group:		Applications/System
%pyrequires_eq	python
Requires:	vmailmgr-daemon = %{version}

%description python
This package contains vmailmgr code written in/for Python, including
one CGI.

%description python -l pl
Ten pakiet zawiera kod vmailmgra napisany w/dla Pythona i jedno CGI.

%package pop3
Summary:	qmail-pop3 config for vmailmgr
Summary(pl):	Konfiguracja qmail-pop3 dla vmailmgr
Group:		Applications/System
Requires:	vmailmgr-daemon = %{version}
Requires:	qmail-pop3
PreReq:		rc-inetd

%description pop3
This package contains configfiles needed for working with qmail pop3
server.

%description pop3 -l pl
Ten pakiet zawiera pliki konfiguracyjne potrzebne do pracy z serwerem
pop3 qmaila.

%package quota
Summary:	Config files needed for per-virtual-user quotas for vmailmgr
Summary(pl):	Pliki konfiguracyjne do quoty dla u¿ytkowników vmailmgr
Group:		Applications/System
Requires:	vmailmgr-daemon = %{version}
Requires:	qmail-pop3

%description quota
This package contains configfiles needed for working with
per-virtual-user quotas.

%description quota -l pl
Ten pakiet zawiera pliki konfiguracyjne potrzebne do quoty dla
u¿ytkowników wirtualnych.

%prep
%setup -q
install %{SOURCE3} doc

%build
%{__aclocal}
%{__autoconf}
%configure
%{__make} all

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/{var/log/vmailmgrd,etc/{rc.d/init.d,vmailmgr,qmail,sysconfig/rc-inetd}}

%python_compile
%python_compile_opt

%{__make} install DESTDIR=$RPM_BUILD_ROOT \
	cgidir=/home/services/httpd/cgi-bin \
	pythonlibdir=%{python_sitepkgsdir}/vmailmgr

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/vmailmgrd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/rc-inetd/qpop-vmailmgr

echo users >$RPM_BUILD_ROOT%{_sysconfdir}/vmailmgr/user-dir
echo passwd >$RPM_BUILD_ROOT%{_sysconfdir}/vmailmgr/password-file
echo ./Maildir/ >$RPM_BUILD_ROOT%{_sysconfdir}/vmailmgr/default-maildir
echo maildir >$RPM_BUILD_ROOT%{_sysconfdir}/vmailmgr/maildir-arg-str
echo /var/lock/svc/vmailmgrd/socket >$RPM_BUILD_ROOT%{_sysconfdir}/vmailmgr/socket-file
echo checkvpw >$RPM_BUILD_ROOT%{_sysconfdir}/qmail/checkpassword

cat << EOF >$RPM_BUILD_ROOT%{_sysconfdir}/vmailmgr/vdeliver-predeliver
#!/bin/sh
%{_bindir}/vcheckquota
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post daemon
/sbin/chkconfig --add vmailmgrd
touch /var/log/vmailmgrd
if [ -f /var/lock/subsys/vmailmgrd ]; then
	/etc/rc.d/init.d/vmailmgrd restart >&2
else
	echo "Run \"/etc/rc.d/init.d/vmailmgrd start\" to start vmailmgrd daemon."
fi

%preun daemon
if [ "$1" = "0" ];then
	if [ -r /var/lock/subsys/vmailmgrd ]; then
		/etc/rc.d/init.d/vmailmgrd stop >&2
	fi
	/sbin/chkconfig --del vmailmgrd
fi

%post pop3
if [ -f /var/lock/subsys/rc-inetd ]; then
	/etc/rc.d/init.d/rc-inetd reload 1>&2
else
	echo "Type \"/etc/rc.d/init.d/rc-inetd start\" to start inet server" 1>&2
fi

%postun pop3
if [ -f /var/lock/subsys/rc-inetd ]; then
	/etc/rc.d/init.d/rc-inetd reload
fi

%files
%defattr(644,root,root,755)
%doc doc/{ChangeLog*,*.txt} doc/{*.html,*.sgml}
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %dir %{_sysconfdir}/vmailmgr
%config(missingok noreplace) %verify(not size mtime md5) %{_sysconfdir}/vmailmgr/*
%{_mandir}/man[1578]/*

%files cgi
%defattr(644,root,root,755)
%attr(755,root,root) /home/services/httpd/cgi-bin/*

%files php
%defattr(644,root,root,755)
/home/services/httpd/php/*

%files daemon
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/vmailmgrd
%attr(755,root,root) %{_sbindir}/vmailmgrd
%attr(700,root,root) %dir /var/log/vmailmgrd

%files python
%defattr(644,root,root,755)
%dir %{python_sitepkgsdir}/vmailmgr
%{python_sitepkgsdir}/vmailmgr/*.pyc
%{python_sitepkgsdir}/vmailmgr/*.pyo

%files pop3
%defattr(644,root,root,755)
%config /etc/sysconfig/rc-inetd/qpop-vmailmgr

%files quota
%defattr(644,root,root,755)
%config %{_sysconfdir}/vmailmgr/vdeliver-predeliver
