%global debug_package %{nil}

# Global variables for github repository
%global commit0 5517c496a7a540a5cf170af3c957e1bb9a0247b2
%global gittag0 master
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:    orbit.lv2
Version: 0.1.0
Release: 3%{?dist}
Summary: LV2 Event Looper
URL:     https://github.com/OpenMusicKontrollers/orbit.lv2
Group:   Applications/Multimedia
License: GPLv2+

Source0: https://github.com/OpenMusicKontrollers/orbit.lv2/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: gcc gcc-c++
BuildRequires: lv2-devel
BuildRequires: meson
BuildRequires: zlib-devel

%description
LV2 Event Looper

%prep
%setup -qn %{name}-%{commit0}

%build

VERBOSE=1 meson --prefix=/usr build
cd build

DESTDIR=%{buildroot} VERBOSE=1 ninja

%install

cd build
DESTDIR=%{buildroot} ninja install

%files
%{_libdir}/lv2/*

%changelog
* Wed Nov 13 2019 Yann Collette <ycollette.nospam@free.fr> - 0.1.0-3
- update to 0.1.0-3

* Mon Oct 15 2018 Yann Collette <ycollette.nospam@free.fr> - 0.1.0-2
- update for Fedora 29

* Sat May 12 2018 Yann Collette <ycollette.nospam@free.fr> - 0.1.0-2
- update to latest master

* Sat Jun 06 2015 Yann Collette <ycollette.nospam@free.fr> - 0.1.0-1
- Initial build
