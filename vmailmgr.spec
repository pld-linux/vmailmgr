Summary:	Simple virtualizing POP3 password interface
Name:		vmailmgr
Version:	0.96.1
Release:	1
Group:		Utilities/System
License:	GPL
Source:		http://em.ca/~bruceg/vmailmgr/archive/%{version}/%{name}-%{version}.tar.gz
Source1:	vmailmgr.initd
URL:		http://em.ca/~bruceg/vmailmgr/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Obsoletes:	checkvpw

%description
Vmailmgr provides a virtualizing password-checking interface to qmail-pop3d 
as well as both a delivery agent to automatically delivery mail within a 
virtual domain and a set of tools to manage such a domain.   

%package cgi
Summary:	CGI applications for vmailmgr
Group:		Utilities/System
Requires:	vmailmgr-daemon = %{PACKAGE_VERSION}

%description cgi
This package contains CGI applications to allow web-based administration of 
vmailmgr systems.   

%package daemon
Summary:	Vmailmgr daemon for CGIs
Group:		Utilities/System

%description daemon
This package contains the vmailmgrd daemon that provides virtual domain 
manipulation services to support unprivileged clients like CGIs.   

%package python
Summary:	Python modules and CGIs for vmailmgr
Group:		Utilities/System
Requires:	python >= 1.5
Requires:	vmailmgr-daemon = %{PACKAGE_VERSION}

%description python
This package contains vmailmgr code written in/for Python, including one 
CGI.   

%prep
%setup -q
CFLAGS="$RPM_OPT_FLAGS"
CXXFLAGS="$RPM_OPT_FLAGS"
LDFLAGS="-s"
%configure

%build
make all

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/{var/log/vmailmgrd,etc/{rc.d/init.d,vmailmgr}}

make install DESTDIR=$RPM_BUILD_ROOT \
	cgidir=/home/httpd/cgi-bin \
	pythonlibdir=%{_libdir}/python1.5

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/vmailmgrd

echo users >user-dir
echo passwd >password-file
echo ./Maildir/ >default-maildir
echo maildir >maildir-arg-str
echo /var/lock/svc/vmailmgrd/socket >socket-file

gzip -9nf doc/ChangeLog* AUTHORS COPYING NEWS doc/TODO doc/YEAR2000 doc/*.txt \
	$RPM_BUILD_ROOT%{_mandir}/man*/*

%clean
rm -rf $RPM_BUILD_ROOT

%post daemon
/sbin/chkconfig --add vmailmgrd

if [ -f /var/lock/subsys/vmailmgrd ]; then
	/etc/rc.d/init.d/vmailmgrd restart >&2
else
	echo "Run \"/etc/rc.d/init.d/vmailmgrd start\" to start vmailmgrd daemon."
fi

%preun daemon
if [ "$1" = "0" ];then
	/sbin/chkconfig --del vmailmgrd
	/etc/rc.d/init.d/vmailmgrd stop >&2
fi

%files
%defattr(644,root,root,755)
%doc {AUTHORS,COPYING,NEWS,doc/{ChangeLog*,TODO,YEAR2000,*.txt}}.gz
%doc doc/*.html
%attr(644,root,root) %{_bindir}/*
%attr(755,root,root) %dir /etc/vmailmgr
%config(missingok noreplace)  %verify(not size mtime md5) /etc/vmailmgr/*
%{_mandir}/man[1578]/*

%files cgi
%defattr(644,root,root,755)
/home/httpd/cgi-bin/*

%files daemon
%defattr(644,root,root,755)
%attr(754,root,root) /etc/rc.d/init.d/vmailmgrd
%attr(755,root,root) %{_sbindir}/vmailmgrd
%attr(700,root,root) /var/log/vmailmgrd

%files python
%defattr(644,root,root,755)
/usr/lib/python1.5/*
