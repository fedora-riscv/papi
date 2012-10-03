%bcond_with bundled_libpfm
Summary: Performance Application Programming Interface
Name: papi
Version: 5.0.1
Release: 2%{?dist}
License: BSD
Group: Development/System
URL: http://icl.cs.utk.edu/papi/
Source0: http://icl.cs.utk.edu/projects/papi/downloads/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: ncurses-devel
BuildRequires: gcc-gfortran
BuildRequires: kernel-headers >= 2.6.32
BuildRequires: chrpath
BuildRequires: lm_sensors-devel
%if %{without bundled_libpfm}
BuildRequires: libpfm-devel >= 4.3.0
BuildRequires: libpfm-static >= 4.3.0
%endif
# Following required for net component
BuildRequires: net-tools
# Following required for inifiband component
BuildRequires: libibmad-devel
#Right now libpfm does not know anything about s390 and will fail
ExcludeArch: s390 s390x

%description
PAPI provides a programmer interface to monitor the performance of
running programs.

%package devel
Summary: Header files for the compiling programs with PAPI
Group: Development/System
Requires: papi = %{version}-%{release}
%description devel
PAPI-devel includes the C header files that specify the PAPI user-space
libraries and interfaces. This is required for rebuilding any program
that uses PAPI.

%package static
Summary: Static libraries for the compiling programs with PAPI
Group: Development/System
Requires: papi = %{version}-%{release}
%description static
PAPI-static includes the static versions of the library files for
the PAPI user-space libraries and interfaces.

%prep
%setup -q

%build
%if %{without bundled_libpfm}
# Build our own copy of libpfm.
%global libpfm_config --with-pfm-incdir=%{_includedir} --with-pfm-libdir=%{_libdir}
%endif

cd src
%configure --with-perf-events \
%{?libpfm_config} \
--with-static-lib=yes --with-shared-lib=yes --with-shlib \
--with-components="appio coretemp example lmsensors lustre mx net rapl stealtime"
#components currently left out because of build configure/build issues
#--with-components="appio cuda vmware"

pushd components
#pushd cuda; ./configure; popd
pushd infiniband; %configure; popd
pushd lmsensors; \
 %configure --with-sensors_incdir=/usr/include/sensors \
 --with-sensors_libdir=%{_libdir}; \
 popd
#pushd vmware; ./configure; popd
popd

#DBG workaround to make sure libpfm just uses the normal CFLAGS
DBG="" make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
cd src
make DESTDIR=$RPM_BUILD_ROOT install

chrpath --delete $RPM_BUILD_ROOT%{_libdir}/*.so*

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig
%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}/*
%{_libdir}/*.so.*
/usr/share/papi
%doc INSTALL.txt README LICENSE.txt RELEASENOTES.txt
%doc %{_mandir}/man1/*

%files devel
%defattr(-,root,root,-)
%{_includedir}/*.h
%if %{with bundled_libpfm}
#%{_includedir}/perfmon/*.h
%endif
%{_libdir}/*.so
%doc %{_mandir}/man3/*

%files static
%defattr(-,root,root,-)
%{_libdir}/*.a

%changelog
* Wed Oct 03 2012 William Cohen <wcohen@redhat.com> - 5.0.1-2
- Make sure using compatible version of libpfm.

* Thu Sep 20 2012 William Cohen <wcohen@redhat.com> - 5.0.1-1
- Rebase to 5.0.1.

* Mon Sep 10 2012 William Cohen <wcohen@redhat.com> - 5.0.0-6
- Back port fixes for Intel Ivy Bridge event presets.

* Thu Aug 30 2012 William Cohen <wcohen@redhat.com> - 5.0.0-5
- Fixes to make papi with unbundled libpfm.

* Mon Aug 27 2012 William Cohen <wcohen@redhat.com> - 5.0.0-2
- Keep libpfm unbundled.

* Fri Aug 24 2012 William Cohen <wcohen@redhat.com> - 5.0.0-1
- Rebase to 5.0.0.

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.4.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jun 11 2012 William Cohen <wcohen@redhat.com> - 4.4.0-4
- Use siginfo_t rather than struct siginfo.

* Mon Jun 11 2012 William Cohen <wcohen@redhat.com> - 4.4.0-3
- Correct build requires.

* Mon Jun 11 2012 William Cohen <wcohen@redhat.com> - 4.4.0-2
- Unbundle libpfm4 from papi.
- Correct description spellings.
- Remove unused test section.

* Fri Apr 20 2012 William Cohen <wcohen@redhat.com> - 4.4.0-1
- Rebase to 4.4.0.

* Fri Mar 9 2012 William Cohen <wcohen@redhat.com> - 4.2.1-2
- Fix overrun in lmsensor component. (rhbz797692)

* Tue Feb 14 2012 William Cohen <wcohen@redhat.com> - 4.2.1-1
- Rebase to 4.2.1.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Nov 02 2011 William Cohen <wcohen@redhat.com> - 4.2.0-3
- Remove unwanted man1/*.c.1 files. (rhbz749725)

* Mon Oct 31 2011 William Cohen <wcohen@redhat.com> - 4.2.0-2
- Include appropirate man pages with papi rpm. (rhbz749725)
- Rebase to papi-4.2.0, fixup for coretemp component. (rhbz746851)

* Thu Oct 27 2011 William Cohen <wcohen@redhat.com> - 4.2.0-1
- Rebase to papi-4.2.0.

* Fri Aug 12 2011 William Cohen <wcohen@redhat.com> - 4.1.3-3
- Provide papi-static.

* Thu May 12 2011 William Cohen <wcohen@redhat.com> - 4.1.3-2
- Use corrected papi-4.1.3.

* Thu May 12 2011 William Cohen <wcohen@redhat.com> - 4.1.3-1
- Rebase to papi-4.1.3

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.1.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 24 2011 William Cohen <wcohen@redhat.com> - 4.1.2.1-1
- Rebase to papi-4.1.2.1

* Fri Oct 1 2010 William Cohen <wcohen@redhat.com> - 4.1.1-1
- Rebase to papi-4.1.1

* Mon Jun 8 2010 William Cohen <wcohen@redhat.com> - 4.1.0-1
- Rebase to papi-4.1.0

* Mon May 17 2010 William Cohen <wcohen@redhat.com> - 4.0.0-5
- Test run with upstream cvs version.

* Wed Feb 10 2010 William Cohen <wcohen@redhat.com> - 4.0.0-4
- Resolves: rhbz562935 Rebase to papi-4.0.0 (correct ExcludeArch).

* Wed Feb 10 2010 William Cohen <wcohen@redhat.com> - 4.0.0-3
- Resolves: rhbz562935 Rebase to papi-4.0.0 (bump nvr).

* Wed Feb 10 2010 William Cohen <wcohen@redhat.com> - 4.0.0-2
- correct the ctests/shlib test
- have PAPI_set_multiplex() return proper value
- properly handle event unit masks
- correct PAPI_name_to_code() to match events
- Resolves: rhbz562935 Rebase to papi-4.0.0 

* Wed Jan 13 2010 William Cohen <wcohen@redhat.com> - 4.0.0-1
- Generate papi.spec file for papi-4.0.0.
