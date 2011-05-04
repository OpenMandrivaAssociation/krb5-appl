# For consistency with regular login.
%global login_pam_service remote

Name: krb5-appl
Version: 1.0.1
Release: %mkrel 2
Summary: Kerberos-aware versions of telnet, ftp, rsh, and rlogin
License: MIT
URL: http://web.mit.edu/kerberos/www/
Group: System/Servers
# Maybe we should explode from the now-available-to-everybody tarball instead?
# http://web.mit.edu/kerberos/dist/krb5-appl/1.0/krb5-appl-1.0-signed.tar
Source0: krb5-appl-%{version}.tar.gz
Source1: krb5-appl-%{version}.tar.gz.asc
Source12: krsh
Source13: krlogin
Source14: eklogin.xinetd
Source15: klogin.xinetd
Source16: kshell.xinetd
Source17: krb5-telnet.xinetd
Source18: gssftp.xinetd
Source22: ekrb5-telnet.xinetd
Source125: krb5-appl-1.0-manpaths.txt
Source26: gssftp.pamd
Source27: kshell.pamd
Source28: ekshell.pamd

Patch0: krb5-appl-1.0-fix-format-errors.patch
Patch3: krb5-1.3-netkit-rsh.patch
Patch4: krb5-appl-1.0-rlogind-environ.patch
Patch11: krb5-1.2.1-passive.patch
Patch14: krb5-1.3-ftp-glob.patch
Patch33: krb5-appl-1.0-io.patch
Patch36: krb5-1.7-rcp-markus.patch
Patch40: krb5-1.4.1-telnet-environ.patch
Patch57: krb5-appl-1.0-login_chdir.patch
Patch160: krb5-appl-1.0-pam.patch
Patch161: krb5-appl-1.0-manpaths.patch
Patch72: krb5-1.6.3-ftp_fdleak.patch
Patch73: krb5-1.6.3-ftp_glob_runique.patch
Patch79: krb5-trunk-ftp_mget_case.patch
Patch88: krb5-1.7-sizeof.patch
Patch89: krb5-appl-1.0.1-largefile.patch
BuildRequires: bison
BuildRequires: flex
BuildRequires: ncurses-devel
BuildRequires: texinfo
BuildRequires: krb5-devel
BuildRequires: pam-devel
BuildRoot: %{_tmppath}/%{name}-%{version}

%description
This package contains Kerberos-aware versions of the telnet, ftp, rcp, rsh,
and rlogin clients and servers.  While these have been replaced by tools
such as OpenSSH in most environments, they remain in use in others.

%package servers
Group: System/Servers
Summary: Kerberos-aware telnet, ftp, rcp, rsh and rlogin servers
Requires: xinetd
Requires(post): /sbin/service, xinetd
# transition with previous package
Obsoletes: telnet-server-krb5
Obsoletes: ftp-server-krb5
Provides:  telnet-server-krb5
Provides:  ftp-server-krb5
# multiple alternatives
Provides:  telnet-server
Conflicts: netkit-telnet-server
Conflicts: heimdal-telnetd

%description servers
This package contains Kerberos-aware versions of the telnet, ftp, rcp, rsh,
and rlogin servers.  While these have been replaced by tools such as OpenSSH
in most environments, they remain in use in others.

%package clients
Summary: Kerberos-aware telnet, ftp, rcp, rsh and rlogin clients
Group: Networking/Remote access
# transition with previous package
Obsoletes: telnet-client-krb5
Obsoletes: ftp-client-krb5
Provides:  telnet-client-krb5
Provides:  ftp-client-krb5
# multiple alternatives
Provides:  telnet-client
Conflicts: netkit-telnet
Conflicts: heimdal-telnet

%description clients
This package contains Kerberos-aware versions of the telnet, ftp, rcp, rsh,
and rlogin clients.  While these have been replaced by tools such as OpenSSH
in most environments, they remain in use in others.

%prep
%setup -q
ln -s NOTICE LICENSE

%patch0 -p1 -b .format
%patch160 -p1 -b .pam
%patch161 -p1 -b .manpaths
%patch3  -p3 -b .netkit-rsh
%patch4  -p1 -b .rlogind-environ
%patch11 -p3 -b .passive
%patch14 -p3 -b .ftp-glob
%patch33 -p1 -b .io
%patch36 -p3 -b .rcp-markus
%patch40 -p3 -b .telnet-environ
%patch57 -p1 -b .login_chdir
%patch72 -p3 -b .ftp_fdleak
%patch73 -p3 -b .ftp_glob_runique
%patch79 -p2 -b .ftp_mget_case
%patch88 -p3 -b .sizeof
%patch89 -p1 -b .largefile

# Rename the man pages so that they'll get generated correctly.  Uses the
# "krb5-appl-1.0-manpaths.txt" source file.
cat %{SOURCE125} | while read manpage ; do
	mv "$manpage" "$manpage".in
done

# Rebuild the configure scripts.
autoheader
autoconf

%build
# Build everything position-independent.
INCLUDES=-I%{_includedir}/et
CFLAGS="`echo $RPM_OPT_FLAGS $DEFINES $INCLUDES -fPIE -fno-strict-aliasing`"
LDFLAGS="-pie"
%configure2_5x \
	CFLAGS="$CFLAGS" \
	LDFLAGS="$LDFLAGS" \
	--with-pam \
	--with-pam-login-service=%{login_pam_service}
%make

%install
rm -rf %{buildroot}

# Shell scripts wrappers for Kerberized rsh and rlogin (source files).
mkdir -p %{buildroot}%{_bindir}
install -m 755 %{SOURCE12} %{buildroot}%{_bindir}
install -m 755 %{SOURCE13} %{buildroot}%{_bindir}

# Xinetd configuration files.
mkdir -p %{buildroot}%{_sysconfdir}/xinetd.d/
for xinetd in \
	%{SOURCE14} \
	%{SOURCE15} \
	%{SOURCE16} \
	%{SOURCE17} \
	%{SOURCE18} \
	%{SOURCE22} ; do
	install -pm 644 ${xinetd} \
	%{buildroot}%{_sysconfdir}/xinetd.d/`basename ${xinetd} .xinetd`
done

# PAM configuration files.
mkdir -p %{buildroot}%{_sysconfdir}/pam.d/
for pam in \
	%{SOURCE26} \
	%{SOURCE27} \
	%{SOURCE28} ; do
	install -pm 644 ${pam} \
	%{buildroot}%{_sysconfdir}/pam.d/`basename ${pam} .pamd`
done

%makeinstall_std

%clean
rm -rf %{buildroot}

%post servers
/sbin/service xinetd reload > /dev/null 2>&1 || :
exit 0

%postun servers
/sbin/service xinetd reload > /dev/null 2>&1 || :
exit 0

%files clients
%defattr(-,root,root,-)
%doc README NOTICE LICENSE

# Used by both clients and servers.
%{_bindir}/rcp
%{_mandir}/man1/rcp.1*

# Client network bits.
%{_bindir}/ftp
%{_mandir}/man1/ftp.1*
%{_bindir}/krlogin
%{_bindir}/rlogin
%{_mandir}/man1/rlogin.1*
%{_bindir}/krsh
%{_bindir}/rsh
%{_mandir}/man1/rsh.1*
%{_bindir}/telnet
%{_mandir}/man1/telnet.1*
%{_mandir}/man1/tmac.doc*

%files servers
%defattr(-,root,root,-)
%doc README NOTICE LICENSE
%docdir %{_mandir}

# Used by both clients and servers.
%{_bindir}/rcp
%{_mandir}/man1/rcp.1*

%config(noreplace) %{_sysconfdir}/xinetd.d/*
%config(noreplace) %{_sysconfdir}/pam.d/kshell
%config(noreplace) %{_sysconfdir}/pam.d/ekshell
%config(noreplace) %{_sysconfdir}/pam.d/gssftp

# Login is used by telnetd and klogind.
%{_sbindir}/login.krb5
%{_mandir}/man8/login.krb5.8*

# Application servers.
%{_sbindir}/ftpd
%{_mandir}/man8/ftpd.8*
%{_sbindir}/klogind
%{_mandir}/man8/klogind.8*
%{_sbindir}/kshd
%{_mandir}/man8/kshd.8*
%{_sbindir}/telnetd
%{_mandir}/man8/telnetd.8*
