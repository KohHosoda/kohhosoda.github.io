#!/usr/local/bin/perl
################################################################################
# 高機能アクセス解析CGI Standard版（アクセスログ ロギング用）
# Ver 3.8.1
# Copyright(C) futomi 2001 - 2004
# http://www.futomi.com/
###############################################################################
require './accconfig.cgi';
use Time::Local;
use CGI;
my $co = new CGI;
$| = 1;


# Remote host
my $remote_host = &GetRemoteHost;


# 指定ホストからのアクセスを除外する
my($Reject);
my $RejectFlag = 0;
if(scalar @REJECT_HOSTS) {
	for $Reject (@REJECT_HOSTS) {
		if($Reject =~ /[^0-9\.]/) {	# ホスト名指定の場合
			if($remote_host =~ /$Reject$/) {
				$RejectFlag = 1;
				last;
			}
		} else {	# IPアドレス指定の場合
			if($ENV{'REMOTE_ADDR'} =~ /^$Reject/) {
				$RejectFlag = 1;
				last;
			}
		}
	}
	if($RejectFlag) {
		&PrintImage;
		exit;
	}
}


my $Time = time + $TIMEDIFF*60*60;
my $DateStr = &TimeStamp($Time);
$DateStr = substr($DateStr, 0, 8);
$MonStr = substr($DateStr, 0, 6);
if($LOTATION == 2) {
	$LOG .= "\.$DateStr\.cgi";
} elsif($LOTATION == 3) {
	$LOG .= "\.$MonStr".'00.cgi';
} else {
	$LOG .= "\.cgi";
}

# Access Log Lotation
if($LOTATION) {
	&LogLotation;
}

# User Tracking
my %CookieList = &GetCookie;
my $TrackingData = $CookieList{'futomiacc'};
my($FirstUserFlag) = 0;
unless($TrackingData) {
	$TrackingData = $ENV{'REMOTE_ADDR'}.'.'.time;
	$FirstUserFlag = 1;
}


# Remote user
my($remote_user) = &GetRemoteUser;

# The date and time of the request
my $date = &TimeStamp($Time);

# Requested URI
my $request = &GetRequest;

# HTTP_REFERER
my $referrer = &GetReferrer;

# Make Log String
my $LogString = &GetLogString;

# Loging
&Loging($LogString);

# Print Image to the Client
&PrintImage;
exit;



######################################################################
#  Subroutine
######################################################################

# Print Image to the Client
sub PrintImage {
	my($logo_size, $data);
	if($ENV{SCRIPT_FILENAME } =~ /png$/) {
		open(IMAGE, "<$JLOGO");
		$logo_size = -s "$JLOGO";
		read IMAGE, $data, $logo_size;
		close IMAGE;
		print $co->header(-type=>'image/png'), $data;
	} else {
		open(IMAGE, "<$LOGO");
		$logo_size = -s "$LOGO";
		read IMAGE, $data, $logo_size;
		close IMAGE;
		print "Pragma: no-cache\n";
		print "Cache-Control: no-cache\n";
		print "P3P: CP=\"NOI ADMa\"\n";
		if($USECOOKIE) {
			$SetCookieString = &SetCookie('futomiacc', $TrackingData, $EXPIREDAYS);
			print "$SetCookieString\n";
		}
		print "Content-Type: image/gif\n\n";
		print $data;
	}
}

sub SetCookie {
	my($CookieName, $CookieValue, $ExpireDays, $Domain, $Path) = @_;
	# URLエンコード
	$CookieValue =~ s/([^\w\=\& ])/'%' . unpack("H2", $1)/eg;
	$CookieValue =~ tr/ /+/;
	my($CookieHeaderString);
	$CookieHeaderString .= "Set-Cookie: $CookieName=$CookieValue\;";
	if($ExpireDays) {
		my(@MonthString) = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
					'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec');
		my(@WeekString) = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');
		my($time) = time + $ExpireDays*24*60*60;
		my($sec, $min, $hour, $monthday, $month, $year, $weekday) = gmtime($time);
		$year += 1900;
		$month = $MonthString[$month];
		if($monthday < 10) {$monthday = '0'.$monthday;}
		if($sec < 10) {$sec = '0'.$sec;}
		if($min < 10) {$min = '0'.$min;}
		if($hour < 10) {$hour = '0'.$hour;}
		my($GmtString) = "$WeekString[$weekday], $monthday-$month-$year $hour:$min:$sec GMT";
 		$CookieHeaderString .= " expires=$GmtString\;";
	}
	if($Domain) {
		$CookieHeaderString .= " domain=$Domain;";
	}
	if($Path) {
		$CookieHeaderString .= " path=$Path;";
	}
	return $CookieHeaderString;
}

sub Loging {
	my($String) = @_;
	open(LOGFILE, ">>$LOG") || &ErrorPrint("ログファイルをオープンできませんでした。ディレクトリ「logs」のパーミッションを確認して下さい。パーミッションを変更したら、ディレクトリ「logs」内にあるファイルをすべて削除してから、再度ブラウザーで acclog.cgi にアクセスしてみて下さい。: $!");
	if(&Lock(LOGFILE)) {
		&ErrorPrint("ログファイルのロック処理に失敗しました。 : $!");
	}
	print LOGFILE "$String\n";
	close(LOGFILE);
}

sub GetLogString {
	my($logfile) = "$date $remote_host $TrackingData $remote_user $request $referrer \"$ENV{'HTTP_USER_AGENT'}\"";
	if($ENV{'HTTP_ACCEPT_LANGUAGE'} eq '') {
		$logfile .= " \"-\"";
	} else {
		$logfile .= " \"$ENV{'HTTP_ACCEPT_LANGUAGE'}\"";
	}
	my $ScreenWidth = $co->param('width');
	my $ScreenHeight = $co->param('height');
	my $ColorDepth = $co->param('color');
	my $ua = $ENV{'HTTP_USER_AGENT'};
	if($ScreenWidth && $ScreenHeight && $ColorDepth) {
		$logfile .= " \"$ScreenWidth $ScreenHeight $ColorDepth\"";
	} elsif($ua =~ /J-PHONE/) {
		if($ENV{'HTTP_X_JPHONE_DISPLAY'} eq '' || $ENV{'HTTP_X_JPHONE_COLOR'} eq '') {
			$logfile .= ' "-"';
		} else {
			my($width, $height) = split(/\*/, $ENV{'HTTP_X_JPHONE_DISPLAY'});
			my $color = $ENV{'HTTP_X_JPHONE_COLOR'};
			$color =~ s/^[^0-9]+//;
			my $depth = log($color) / log(2);
			$logfile .= " \"$width $height $depth\"";
		}
	} elsif($ua =~ /UP\.Browser/) {
		if($ENV{'HTTP_X_UP_DEVCAP_SCREENDEPTH'} eq '' || $ENV{'HTTP_X_UP_DEVCAP_SCREENPIXELS'} eq '') {
			$logfile .= ' "-"';
		} else {
			my($width, $height) = split(/,/, $ENV{'HTTP_X_UP_DEVCAP_SCREENPIXELS'});
			my($depth) = split(/,/, $ENV{'HTTP_X_UP_DEVCAP_SCREENDEPTH'});
			$logfile .= " \"$width $height $depth\"";
		}
	} elsif($ua =~ /^PDXGW\/[0-9\.]+\s*\(([^\)]+)\)/) {
		#PDXGW/1.0 (TX=8;TY=7;GX=96;GY=84;C=C256;G=BF;GI=2)
		my $tmp = $1;
		my @devinfos = split(/;/, $tmp);
		my($x, $y, $c);
		for my $key (@devinfos) {
			my($name, $value) = split(/=/, $key);
			if($name eq 'GX') {
				$x = $value;
			} elsif($name eq 'GY') {
				$y = $value;
			} elsif($name eq 'C') {
				if($value eq 'CF') {
					$c = '16';
				} elsif($value eq 'C256') {
					$c = '8';
				} elsif($value eq 'C4') {
					$c = '2';
				} elsif($value eq 'G2') {
					$c = '1';
				} else {
					$c = '';
				}
			}
		}
		$logfile .= " \"$x $y $c\"";
	} else {
		$logfile .= ' "-"';
	}
	return $logfile;
}


sub GetReferrer {
	my @query_parts = split(/&/, $ENV{'QUERY_STRING'});
	my $referrer;
	my $part;
	my $flag = 0;
	for $part (@query_parts) {
		if($part =~ /^(width|height|color)=/i) {
			$flag = 0;
		}
		if($part =~ /^referrer=/i) {
			$flag = 1;
		}
		if($flag) {
			$part =~ s/^referrer=//;
			$referrer .= "$part&";
		}
	}
	$referrer =~ s/&$//;
	if($referrer eq '') {
		$referrer = '-';
	}
	$referrer =~ s/\%7e/\~/ig;
	return $referrer;
}

sub URL_encode {
	my($str) = @_;
	$str =~ s/([^\w\=\&\# ])/'%' . unpack("H2", $1)/eg;
	$str =~ tr/ /+/;
	$str =~ s/(\&)(\#)/'%' . unpack("H2", $1) . '%' . unpack("H2", $2)/eg;
	$str =~ s/(\#)/'%' . unpack("H2", $1)/eg;
	return $str;
}


sub TimeStamp {
	my($time) = @_;
	my($sec, $min, $hour, $mday, $mon, $year) = localtime($time);
	$year += 1900;
	$mon += 1;
	$mon = "0$mon" if($mon < 10);
	$mday = "0$mday" if($mday < 10);
	$hour = "0$hour" if($hour < 10);
	$min = "0$min" if($min < 10);
	$sec = "0$sec" if($sec < 10);
	my($stamp) = $year.$mon.$mday.$hour.$min.$sec;
	return $stamp;
}


sub Lock {
	local(*FILE) = @_;
	eval{flock(FILE, 2)};
	if($@) {
		return $!;
	} else {
		return '';
	}
}

sub GetRequest {
	my($request) = $co->param('url');
	unless($request) {
		if($ENV{'HTTP_REFERER'} eq '') {
			$request = '-';
		} else {
			$request = $ENV{'HTTP_REFERER'};
		}
	}
	$request =~ s/\%7e/\~/ig;
	return $request;
}

sub GetRemoteUser {
	my($remote_user);
	if($ENV{'REMOTE_USER'} eq '') {
		$remote_user = '-';
	} else {
		$remote_user = $ENV{'REMOTE_USER'};
	}
	return $remote_user;
}

sub GetRemoteHost {
	my($remote_host);
	if($ENV{'REMOTE_HOST'} =~ /[^0-9\.]/) {
		$remote_host = $ENV{'REMOTE_HOST'};
	} else {
		my(@addr) = split(/\./, $ENV{'REMOTE_ADDR'});
		my($packed_addr) = pack("C4", $addr[0], $addr[1], $addr[2], $addr[3]);
		my($aliases, $addrtype, $length, @addrs);
		($remote_host, $aliases, $addrtype, $length, @addrs) = gethostbyaddr($packed_addr, 2);
		unless($remote_host) {
			$remote_host = $ENV{'REMOTE_ADDR'};
		}
	}
	return $remote_host;
}

sub LogLotation {
	my $DateStr = &TimeStamp($Time);
	$DateStr = substr($DateStr, 0, 8);
	my $log_size = -s "$LOG";
	if($LOTATION == 1) {
		if($log_size > $LOTATION_SIZE) {
			if($LOTATION_SAVE) {
				rename("$LOG", "$LOG\.$DateStr\.cgi");
			} else {
				unlink("$LOG");
			}
		}
	} elsif($LOTATION == 2 || $LOTATION == 3) {
		unless($LOTATION_SAVE) {
			my @parts = split(/\//, $LOG);
			my $logname = pop @parts;
			my($logname_key) = split(/\./, $logname);
			my $logdir = join('/', @parts);
			if(opendir(DIR, "$logdir")) {
				my @files = readdir(DIR);
				closedir(DIR);
				my $file;
				for $file (@files) {
					if($file eq $logname) {
						next;
					}
					if($file =~ /^$logname_key/) {
						unlink("$logdir/$file");
					}
				}
			}
		}
	}
}

sub GetCookie {
	my(@CookieList) = split(/\; /, $ENV{'HTTP_COOKIE'});
	my(%Cookie) = ();
	my($key, $CookieName, $CookieValue);
	for $key (@CookieList) {
		($CookieName, $CookieValue) = split(/=/, $key);
		$CookieValue =~ s/\+/ /g;
		$CookieValue =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C",hex($1))/eg;
		$Cookie{$CookieName} = $CookieValue;
	}
	return %Cookie;
}

sub ErrorPrint {
	my($Message) = @_;
	print $co->header;
	print "$Message";
	exit;
}

