# Global variables for github repository
%global commit0 6712fcc6f175154b0bf87d2ef4faebedc7cc2ed5
%global gittag0 master
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Summary: Pattern-controlled MIDI amp & time stretch LV2 plugin to produce shuffle / swing effects
Name:    lv2-BSchaffl
Version: 0.1.0
Release: 1%{?dist}
License: GPL
URL:     https://github.com/sjaehn/BSchaffl

Source0: https://github.com/sjaehn/BSchaffl/archive/%{commit0}.tar.gz#/BSchaffl-%{shortcommit0}.tar.gz

BuildRequires: gcc gcc-c++
BuildRequires: lv2-devel
BuildRequires: libX11-devel
BuildRequires: xcb-util-keysyms-devel
BuildRequires: cairo-devel

%description
Pattern-controlled MIDI amp & time stretch LV2 plugin to produce shuffle / swing effects

%prep
%autosetup -n BSchaffl-%{commit0}

%build

%make_build PREFIX=%{_prefix}r LV2DIR=%{_libdir}/lv2 DESTDIR=%{buildroot} CXXFLAGS="%{build_cxxflags} -std=c++11 -fvisibility=hidden -fPIC"

%install

%make_install PREFIX=%{_prefix}r LV2DIR=%{_libdir}/lv2 DESTDIR=%{buildroot} CXXFLAGS="%{build_cxxflags} -std=c++11 -fvisibility=hidden -fPIC"

%files
%doc README.md
%license LICENSE
%{_libdir}/lv2/*

%changelog
* Mon May 25 2020 Yann Collette <ycollette dot nospam at free.fr> 0.1.0-1
- initial release 
