#!/usr/local/bin/perl
################################################################################
# ���@�\�A�N�Z�X���CGI Standard�Łi��͌��ʕ\���p�j
# Ver 3.8.1
# Copyright(C) futomi 2001 - 2004
# http://www.futomi.com/
###############################################################################

my $COPYRIGHT = '<table border="0" cellpadding="5"><tr><td class=ListHeader4>
<A HREF="http://www.futomi.com/"><font color="#FFFFFF">futomi\'s CGI Cafe ���@�\�A�N�Z�X���CGI Standard�� Ver 3.8</font></a>
</td></tr></table>
';
use Time::Local;
unless(-e './jcode.pl') {
	&ErrorPrint('jcode.pl������܂���B');
}
unless(-e './accconfig.cgi') {
	&ErrorPrint('accconfig.cgi������܂���B');
}
#Perl5.8�ȏ�̏ꍇ�Ɍ���AEncode���W���[�������[�h
my $ENCODE_MODULE_FLAG = 0;
if($] >= 5.008) {
	eval {
		require Encode;
		require Encode::Guess;
	};
	unless($@) {
		$ENCODE_MODULE_FLAG = 1;
	}
}
require './accconfig.cgi';
require './jcode.pl';
use CGI;
$| = 1;

my $query = new CGI;
my $mode = $query->param('MODE');
my $ana_month = $query->param('MONTH');
my $ana_day = $query->param('DAY');
$ana_day =~ s/^0*//;

# ����CGI��URL����肷��B
my $CGI_URL;
if($MANUAL_CGIURL =~ /^http/) {
	$CGI_URL = $MANUAL_CGIURL;
} else {
	$CGI_URL = &GetCgiUrl;
}

# �p�X���[�h�F��
my $CRYPTED_PASS;
if($AUTHFLAG) {
	my $in_pass = $query->param('PASS');
	my %cookies = &GetCookie;
	if($in_pass ne '') {
		$CRYPTED_PASS = &EncryptPasswd($in_pass);
	} elsif($cookies{'PASS'} ne '') {
		$CRYPTED_PASS = $cookies{'PASS'};
	} else {
		&PrintAuthForm();
	}
	unless(&Auth($CRYPTED_PASS)) {
		&PrintAuthForm(1);
	}
}

# �j�����`����B
my @week_map = ('��', '��', '��', '��', '��', '��', '�y');

# ��`�t�@�C����ǂݎ��
my %tld_list = &ReadDef('country_code.dat');
my %langcode_list = &ReadDef('language.dat');

# �ߋ����O���X�g���擾����
my %LogList = &GetPastLogList;

# ��͑Ώۂ̃��O�f�B���N�g���A���O�t�@�C�������
my($SelectedLogFile, $SelectedLogFileName) = &GetSelectedLogFile;

# ���͒l�`�F�b�N
&InputCheck;

# ���O�t�@�C����ǂݎ��
if(-e $SelectedLogFile) {
	open(LOGFILE, "$SelectedLogFile") || &ErrorPrint("�A�N�Z�X���O�u$SelectedLogFile�v���I�[�v���ł��܂���ł���");
} else {
	&ErrorPrint("�A�N�Z�X���O�i$SelectedLogFile�j������܂���B");
}

my($date_check, $RemoteHostBuff, $CookieBuff, $RequestBuff, $RefererBuff, $UserAgentBuff, $AcceptLangBuff, $ScreenBuff);
my(%all_date, %date, %remote_host, %request, %referer, %user_agent, %accept_language, %screen);
my($date_check_mon, $date_check_day);
my $i = 0;
while(<LOGFILE>) {
	chop;
	next if($_ eq '');

	if(/^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\"([^\"]+)\"\s+\"([^\"]+)\"\s+\"([^\"]+)\"/) {
		$date_check = $1;
		$RemoteHostBuff = $2;
		$CookieBuff = $3;
		$RequestBuff = $5;
		$RefererBuff = $6;
		$UserAgentBuff = $7;
		$AcceptLangBuff = $8;
		$ScreenBuff = $9;
	} else {
		next;
	}

	next if($date_check eq '');
	$all_date{$i} = $date_check;
	$date_check_mon = substr($date_check, 0, 6);
	$date_check_day = substr($date_check, 6, 2);
	$date_check_day =~ s/^0//;
	if($mode eq 'MONTHLY' || $mode eq 'DAILY') {
		next unless($date_check_mon eq $ana_month);
		if($mode eq 'DAILY') {
			next unless($date_check_day eq $ana_day);
		}
	}
	$date{$i} = $date_check;
	$remote_host{$i} = lc $RemoteHostBuff;
	$request{$i} = $RequestBuff;
	$referer{$i} = $RefererBuff;
	$user_agent{$i} = $UserAgentBuff;
	$accept_language{$i} = lc $AcceptLangBuff;
	$screen{$i} = $ScreenBuff;

	$i ++;
}
close(LOGFILE);
my $loglines = $i;


# �Ώۃ��O���̃`�F�b�N
unless($loglines >= 1) {
	&ErrorPrint('�Ώۂ̃��O���ꌏ������܂���B');
}

# �Ώۃ��O�̒����J�n���ƒ����I�����𒲂ׂ�
my($min_date, $max_date);
($min_date, $max_date) = &AnalyzeDateRange;

# ���O�t�@�C���̃T�C�Y�𒲂ׂ�(�o�C�g)
my $log_size = &AnalyzeLogfileSize($SelectedLogFile);

# �w�b�_�[�o��
&HtmlHeader;

# ��͊T�v���o��
&PrintSummary;

# �����N�o��
&PrintLink;


# �A�N�Z�X��HOST���A���������L���O�𒲂ׂ�
if($ANA_REMOTETLD || $ANA_REMOTEDOMAIN || $ANA_REMOTEHOST) {
	&AnalyzeRemoteHost;
	if($ANA_REMOTETLD) {	# �A�N�Z�X���g�b�v���x���h���C���iTLD�j���o��
		&PrintRemoteTLD;
	}
	if($ANA_REMOTEDOMAIN) {	# �A�N�Z�X���h���C�������o��
		&PrintRemoteDomain;
	}
	if($ANA_REMOTEHOST) {	# �A�N�Z�X���z�X�g�����o��
		&PrintRomoteHost;
	}
}

# �u���E�U�[�\���\����ꗗ�𒲂ׂ�
if($ANA_HTTPLANG) {
	%language_list = &AnalyzeAcceptLang;
	# �u���E�U�[�\���\���ꃌ�|�[�g���o��
	&PrintHttpLang;
}

# OS, �u���E�U�[�𒲂ׂ�
if($ANA_BROWSER || $ANA_PLATFORM) {
	&AnalyzeUserAgent;
	if($ANA_BROWSER) {	# �u���E�U�[���|�[�g���o��
		&PrintHttpUserAgentBrowser;
	}
	if($ANA_PLATFORM) {	# �v���b�g�t�H�[�����|�[�g���o��
		&PrintHttpUserAgentPlatform;
	}
}

# ���ԕʁA�j���ʁA���t�ʁA���ʃ��N�G�X�g���𒲂ׂ�
if($ANA_REQUESTMONTHLY || $ANA_REQUESTDAILY || $ANA_REQUESTHOURLY || $ANA_REQUESTWEEKLY) {
	&AnalyzeRequestDate;
	if($ANA_REQUESTMONTHLY) {
		# ���ʃ��N�G�X�g�����|�[�g
		# �S�w���̓��[�h�̏ꍇ�ɂ̂ݏo�͂���B
		if($mode eq '') {
			&PrintRequestMonthly;
		}
	}
	if($ANA_REQUESTDAILY) {
		# ���t�ʃ��N�G�X�g�����|�[�g
		# ���w���̓��[�h�̏ꍇ�ɂ̂ݏo�͂���B
		if($mode eq 'MONTHLY') {
			&PrintRequestDaily;
		}
	}
	if($ANA_REQUESTHOURLY) {
		# ���ԕʃA�N�Z�X�����|�[�g
		&PrintRequestHourly;
	}
	if($ANA_REQUESTWEEKLY) {
		# �j���ʃA�N�Z�X�����|�[�g
		unless($mode eq 'DAILY') {
			&PrintRequestWeekly;
		}
	}
}

# Request Report �𒲂ׂ�
if($ANA_REQUESTFILE) {
	&AnalyzeRequestResource;
	# Request Report ���o��
	&PrintRequestFile;
}

# �����N��URL�A�����G���W���̌����L�[���[�h�𒲂ׂ�
if($ANA_REFERERSITE || $ANA_REFERERURL || $ANA_KEYWORD) {
	&AnalyzeReferer;
	if($ANA_REFERERSITE) {
		# �����N���T�C�g���|�[�g
		&PrintRefererSite;
	}
	if($ANA_REFERERURL) {
		# �����N��URL���o��
		&PrintRefererUrl;
	}
	if($ANA_KEYWORD) {
		# �����G���W���̌����L�[���[�h���o��
		&PrintKeyword;
	}
}

# �X�N���[�����𒲂ׂ�
if($ANA_RESOLUTION || $ANA_COLORDEPTH || $ANA_VIDEOMEMORY) {
	&AnalyzeScreen;
	if($ANA_RESOLUTION) {
		# ��ʉ𑜓x���o��
		&PrintResolution;
	}
	if($ANA_COLORDEPTH) {
		# ��ʐF�[�x���o��
		&PrintColorDepth;
	}
	if($ANA_VIDEOMEMORY) {
		# �r�f�I�������[�T�C�Y����o��
		&PrintVideoMemory;
	}
}


# �����N�o��
&PrintLink;

# �t�b�^�[���o��
&HtmlFooter;

exit;




sub AnalyzeDateRange {
	# �Ώۃ��O�̒����J�n���ƒ����I�����𒲂ׂ�
	my($min_date) = 99999999999999;
	my($max_date) = 0;
	my($i);
	for $i (keys(%date)) {
		if($all_date{$i} > $max_date) {
			$max_date = $date{$i};
		}
		if($date{$i} < $min_date) {
			$min_date = $date{$i};
		}
	}
	return($min_date, $max_date);
}

# ���O�t�@�C���̃T�C�Y�𒲂ׂ�(KB)
sub AnalyzeLogfileSize {
	my($File) = @_;
	my(@log_stat) = stat($File);
	my($log_size) = $log_stat[7];
	return $log_size;
}

# �A�N�Z�X���z�X�g���A�h���C�����A���������L���O�𒲂ׂ�
sub AnalyzeRemoteHost {
	my($i, $tld, $sld, $thld, @dom_buff);
	for $i (keys(%remote_host)) {
		$host_list{$remote_host{$i}} ++;
		@dom_buff = split(/\./, $remote_host{$i});
		$tld = pop(@dom_buff);
		if($tld eq '' || $tld =~ /[^a-zA-Z]/) {
			$country_list{'?'} ++;
		} else {
			$country_list{$tld} ++;
		}
		if($tld eq '') {
			$domain_list{'?'} ++;
		} elsif($tld =~ /[^a-zA-Z]/) {
			$domain_list{'?'} ++;
		} else {
			my $domain = &GetDomainByHostname($remote_host{$i});
			$domain_list{$domain} ++;
		}
	}
}

sub GetDomainByHostname {
	my($host) = @_;
	my %tld_fix = (
		'com' =>'2', 'net'=>'2', 'org'=>'2', 'biz'=>'2', 'info'=>'2', 'name'=>'3',
		'aero'=>'2', 'coop'=>'2', 'museum'=>'2', 'pro'=>'3', 'edu'=>'2', 'gov'=>'2',
		'mil'=>'2', 'int'=>'2', 'arpa'=>'2', 'nato'=>'2',
		'hk'=>'3', 'sg'=>'3', 'kr'=>'3', 'uk'=>'3'
	);
	my %sld_fix = (
		#���{
		'ac.jp'=>'3', 'ad.jp'=>'3', 'co.jp'=>'3', 'ed.jp'=>'3', 'go.jp'=>'3',
		'gr.jp'=>'3', 'lg.jp'=>'3', 'ne.jp'=>'3', 'or.jp'=>'3',
		'hokkaido.jp'=>'3', 'aomori.jp'=>'3', 'iwate.jp'=>'3', 'miyagi.jp'=>'3',
		'akita.jp'=>'3', 'yamagata.jp'=>'3', 'fukushima.jp'=>'3', 'ibaraki.jp'=>'3',
		'tochigi.jp'=>'3', 'gunma.jp'=>'3', 'saitama.jp'=>'3', 'chiba.jp'=>'3',
		'tokyo.jp'=>'3', 'kanagawa.jp'=>'3', 'niigata.jp'=>'3', 'toyama.jp'=>'3',
		'ishikawa.jp'=>'3', 'fukui.jp'=>'3', 'yamanashi.jp'=>'3', 'nagano.jp'=>'3',
		'gifu.jp'=>'3', 'shizuoka.jp'=>'3', 'aichi.jp'=>'3', 'mie.jp'=>'3',
		'shiga.jp'=>'3', 'kyoto.jp'=>'3', 'osaka.jp'=>'3', 'hyogo.jp'=>'3',
		'nara.jp'=>'3', 'wakayama.jp'=>'3', 'tottori.jp'=>'3', 'shimane.jp'=>'3',
		'okayama.jp'=>'3', 'hiroshima.jp'=>'3', 'yamaguchi.jp'=>'3', 'tokushima.jp'=>'3',
		'kagawa.jp'=>'3', 'ehime.jp'=>'3', 'kochi.jp'=>'3', 'fukuoka.jp'=>'3',
		'saga.jp'=>'3', 'nagasaki.jp'=>'3', 'kumamoto.jp'=>'3', 'oita.jp'=>'3',
		'miyazaki.jp'=>'3', 'kagoshima.jp'=>'3', 'okinawa.jp'=>'3', 'sapporo.jp'=>'3',
		'sendai.jp'=>'3', 'chiba.jp'=>'3', 'yokohama.jp'=>'3', 'kawasaki.jp'=>'3',
		'nagoya.jp'=>'3', 'kyoto.jp'=>'3', 'osaka.jp'=>'3', 'kobe.jp'=>'3',
		'hiroshima.jp'=>'3', 'fukuoka.jp'=>'3', 'kitakyushu.jp'=>'3',
		#��p
		'com.tw'=>'3', 'net.tw'=>'3', 'org.tw'=>'3', 'idv.tw'=>'3', 'game.tw'=>'3',
		'ebiz.tw'=>'3', 'club.tw'=>'3',
		#����
		'com.cn'=>'3', 'net.cn'=>'3', 'org.cn'=>'3', 'gov.cn'=>'3', 'ac.cn'=>'3',
		'edu.cn'=>'3'
	);
	my($level3, $level2, $level1) = $host =~ /([^\.]+)\.([^\.]+)\.([^\.]+)$/;
	my $org_domain;
	if(my $dom_level = $tld_fix{$level1}) {
		if($dom_level eq '2') {
			$org_domain = "${level2}.${level1}";
		} else {
			$org_domain = "${level3}.${level2}.${level1}";
		}
	} elsif($sld_fix{"${level2}.${level1}"}) {
		$org_domain = "${level3}.${level2}.${level1}";
	} else {
		$org_domain = "${level2}.${level1}";
	}
	return $org_domain;
}

# �u���E�U�[�\���\����ꗗ�𒲂ׂ�
sub AnalyzeAcceptLang {
	my(%language_list, $i ,@buff, $max, $j, $lang_tmp, $value_tmp, $lang, $value);
	for $i (keys(%accept_language)) {
		@buff = split(/,/, $accept_language{$i});
		$max = 0;
		undef $lang;
		for $j (@buff) {
			($lang_tmp, $value_tmp) = split(/\;/, $j);
			$value_tmp =~ s/q=//;
			$value_tmp = 1 if($value_tmp eq '');
			if($max < $value_tmp) {
				$lang = $lang_tmp;
				$value = $value_tmp;
				$max = $value_tmp;
			}
		}
		$language_list{"\L$lang"} ++;
	}
	return %language_list;
}

sub AnalyzeUserAgent {
	# OS, �u���E�U�[�𒲂ׂ�
	my($ua, $platform, $platform_v, $browser, $browser_v);
	for $ua (keys(%user_agent)) {
		($platform, $platform_v, $browser, $browser_v) = &User_Agent($user_agent{$ua});
		$browser_list{$browser} ++;
		$browser_v_list{"$browser:$browser_v"} ++;
		$platform_list{"$platform"} ++;
		$platform_v_list{"$platform:$platform_v"} ++;
	}
}

sub AnalyzeRequestDate {
	# ���ԕʁA�j���ʁA���t�ʁA���ʃ��N�G�X�g���𒲂ׂ�
	my($hourly, $daily_y, $daily_m, $daily_d, @daily_array);
	for $key (keys(%date)) {
		$hourly = substr($date{$key}, 8, 2);
		$hourly_list{$hourly} ++;

		$daily_y = substr($date{$key}, 0, 4);
		$daily_m = substr($date{$key}, 4, 2);
		$daily_d = substr($date{$key}, 6, 2);
		@daily_array = localtime(timelocal(0, 0, 0, $daily_d, $daily_m - 1, $daily_y));
		$daily_list{$daily_array[6]} ++;
		$date_list{"$daily_y$daily_m$daily_d"} ++;
		$monthly_list{"$daily_y$daily_m"} ++;
	}
}

sub AnalyzeRequestResource {
	# Directory Report, Request Report �𒲂ׂ�
	my(@req_buff, $req_dir, $cnt, $uri);
	my($HtmlFilePath, $Index,$FileTest, $HitFlag, $RequestUri);
	for $key (keys(%request)) {
		if($request{$key} =~ /^http:\/\/[^\/]+$/) {
			$request{$key} .= '/';
		}
		if($request{$key} =~ /\/$/) {
			$_ = $request{$key};
			m|^https*://[^\/]+/(.*)$|;
			$RequestUri = "/$1";
			$HtmlFilePath = $ENV{'DOCUMENT_ROOT'}.$RequestUri;
			$HitFlag = 0;
			for $Index (@DIRECTORYINDEX) {
				$FileTest = $HtmlFilePath.$Index;
				if(-e $FileTest) {
					$uri = $request{$key}.$Index;
					$HitFlag = 1;
					last;
				}
			}
			unless($HitFlag) {$uri = $request{$key};}
		} else {
			$uri = $request{$key};
		}
		$request_list{$uri} ++;
	}
}

sub AnalyzeReferer {
# �����N��URL�A�����G���W���̌����L�[���[�h�𒲂ׂ�
	my($key, $url, $getstr, @parts, $part, $name, $value, %variables, $word, $decode_str);
	for $key (keys(%referer)) {
		next if($referer{$key} eq '');
		next unless($referer{$key} =~ /^http/);
		$referer_list{$referer{$key}} ++;

		($url, $getstr) = split(/\?/, $referer{$key});
		next if($getstr eq '' && $url !~ /a9\.com/);
		@parts = split(/\&/, $getstr);
		%variables = ();
		for $part (@parts) {
			($name, $value) = split(/=/, $part);
			$variables{$name} = $value;
		}

		$word = '';
		if($url =~ /lycos/) {
			if($url =~ /wisenut/) {
				$word = $variables{'q'};
			} else {
				$word = $variables{'query'};
			}
		} elsif($url =~ /\.google\./) {
			if($variables{'q'}) {
				$word = $variables{'q'};
			} elsif($variables{'as_q'}) {
				$word = $variables{'as_q'};
			}
		} elsif($url =~ /\.yahoo\./) {
			$word = $variables{'p'};
		} elsif($url =~ /\.excite\./) {
			$word = $variables{'s'};
			unless($word) {
				$word = $variables{'search'};
			}
		} elsif($url =~ /\.msn\./) {
			$word = $variables{'q'};
		} elsif($url =~ /\.infoseek\./) {
			$word = $variables{'qt'};
		} elsif($url =~ /\.goo\.ne\.jp/) {
			$word = $variables{'MT'};
		} elsif($url =~ /search\.livedoor\.com/) {
			$word = $variables{'q'};
		} elsif($url =~ /a9\.com\/([^\/]+)/) {
			$word = $1;
			if($word eq '-') {
				$word = '';
			}
		} elsif($url =~ /search\.fresheye\.com/) {
			$word = $variables{'kw'};
		} elsif($url =~ /search\.biglobe\.ne\.jp/) {
			$word = $variables{'q'};
		} elsif($url =~ /search\.netscape\.com/) {
			$word = $variables{'query'};
		} elsif($url =~ /search\.netscape\.com/) {
			$word = $variables{'search'};
		} elsif($url =~ /www\.overture\.com/) {
			$word = $variables{'Keywords'};
		} elsif($url =~ /\.altavista\.com/) {
			$word = $variables{'q'};
		} elsif($url =~ /search\.[a-zA-Z]+\.aol\.com/) {
			$word = $variables{'query'};
		} elsif($url =~ /search\.looksmart\.com/) {
			$word = $variables{'qt'};
		} elsif($url =~ /bach\.istc\.kobe\-u\.ac\.jp\/cgi\-bin\/metcha\.cgi/) {
			$word = $variables{'q'};
		} elsif($url =~ /\.alltheweb\.com/) {
			$word = $variables{'q'};
		} elsif($url =~ /\.blueglobus\.com\/cgi-bin\/search\/search\.cgi/) {
			$word = $variables{'keywords'};
		} elsif($url =~ /\.alexa\.com\/search/) {
			$word = $variables{'q'};
		}
		next if($word eq '');
		$decode_str = &URL_Decode($word);
		if($ENCODE_MODULE_FLAG) {
			eval {
				my $enc = &Encode::Guess::guess_encoding($decode_str, qw/ utf8 euc-jp shiftjis 7bit-jis /);
				my $charset_from= $enc->name;
				&Encode::from_to($decode_str, "$charset_from", "shiftjis");
			};
			if($@) {
				&jcode::convert(\$decode_str, "sjis");
			}
		} else {
			&jcode::convert(\$decode_str, "sjis");
		}
		$decode_str =~ s/\x81\x40/ /g;
		$decode_str =~ s/\s+/ /g;
		$decode_str =~ s/^\s//;
		$decode_str =~ s/\s$//;
		$search_word{$decode_str} ++;

	}
}

sub AnalyzeScreen {
	for $key (keys(%screen)) {
		if($screen{$key} eq '-' || $screen{$key} eq '') {
			next;
		}
		($ScreenWidth, $ScreenHeight, $ColorDepth) = split(/\s/, $screen{$key});
		$ScreenResolution{"$ScreenWidth�~$ScreenHeight"} ++;
		$ScreenColorDepth{"$ColorDepth"} ++;
		$VideoMemorySize = (int($ScreenWidth * $ScreenHeight * $ColorDepth * 10 / 8 / 1024 / 1024)) / 10;
		unless( ($VideoMemorySize*10)%10 == 0) {
			$VideoMemorySize = int($VideoMemorySize) + 1;
		}
		$VideoMemory{$VideoMemorySize} ++;
	}
}

sub PrintSummary {
	my($min_year) = substr($min_date, 0, 4);
	my($min_mon) = substr($min_date, 4, 2);
	my($min_mday) = substr($min_date, 6, 2);
	my($min_hour) = substr($min_date, 8, 2);
	my($min_min) = substr($min_date, 10, 2);
	my($min_sec) = substr($min_date, 12, 2);
	my($max_year) = substr($max_date, 0, 4);
	my($max_mon) = substr($max_date, 4, 2);
	my($max_mday) = substr($max_date, 6, 2);
	my($max_hour) = substr($max_date, 8, 2);
	my($max_min) = substr($max_date, 10, 2);
	my($max_sec) = substr($max_date, 12, 2);

	# �Ώۃ��O���̑Ώی��̃��X�g���쐬����
	my(%year_mon_list, $year_mon);
	for $i (keys(%all_date)) {
		$year_mon = substr($all_date{$i}, 0, 6);
		$year_mon_list{$year_mon} ++;
	}

	print "<HR>\n";
	print '<B class="size4">�T�v</B>',"\n";
	print "<TABLE BORDER=\"0\">\n";

	# �y�[�W�r���[���o��
	print "<TR>\n";
	print "  <TD BGCOLOR=\"#3A6EA5\" CLASS=ListHeader><B><FONT COLOR=\"#FFFFFF\">�y�[�W�r���[</FONT></B></TD>\n";
	my $disp_loglines = &CommaFormat($loglines);
	print "  <TD BGCOLOR=\"#EAEAEA\" ALIGN=\"left\">$disp_loglines</TD>\n";
	print "</TR>\n";

	# ���O�t�@�C�����o��
	print "<form action=\"$CGI_URL\" method=\"POST\">\n";
	print "<TR>\n";
	print "  <TD BGCOLOR=\"#3A6EA5\" CLASS=ListHeader><B><FONT COLOR=\"#FFFFFF\">���O�t�@�C��</FONT></B></TD>\n";
	print "  <TD BGCOLOR=\"#EAEAEA\" ALIGN=\"left\">\n";
	print '    <select name="LOG">',"\n";
	for $key (sort(keys(%LogList))) {
		if($key eq $SelectedLogFileName) {
			print "    <option value=\"$key\" selected>$key</option>\n";
		} else {
			print "    <option value=\"$key\">$key</option>\n";
		}
	}
	print "    </select>\n";
	print "    <input type=\"submit\" VALUE=\"���O�ؑ�\" NAME=\"LOGSELECT\">\n";
	print "  </TD>\n";
	print "</TR>\n";
	print "</form>\n";

	# ���O�t�@�C���T�C�Y���o��
	my $disp_log_size = &CommaFormat($log_size);
	print "<TR>\n";
	print "  <TD BGCOLOR=\"#3A6EA5\" CLASS=ListHeader><B><FONT COLOR=\"#FFFFFF\">���O�t�@�C���T�C�Y</FONT></B></TD>\n";
	print "  <TD BGCOLOR=\"#EAEAEA\" ALIGN=\"left\">$disp_log_size �o�C�g</TD>\n";
	print "</TR>\n";

	# ���O���[�e�[�V�������o��
	my($LogSizeRate) = int(($log_size * 100 / $LOTATION_SIZE) * 10) / 10;
	if($LogSizeRate > 100) {$LogSizeRate = 100;}
	my($LogSizeGraphMaxLen) = 150;	#�s�N�Z��
	my($LogSizeGraphLen) = int($LogSizeGraphMaxLen * $LogSizeRate / 100);	#�s�N�Z��
	print "<TR>\n";
	print "  <TD BGCOLOR=\"#3A6EA5\" CLASS=ListHeader><B><FONT COLOR=\"#FFFFFF\">���O���[�e�[�V����</FONT></B></TD>\n";
	print "  <TD BGCOLOR=\"#EAEAEA\">\n";
	if($LOTATION eq '0') {
		print "���[�e�[�V�������Ȃ�\n";
	} elsif($LOTATION eq '1') {
		my $disp_lotation_size = &CommaFormat($LOTATION_SIZE);
		print "    $disp_lotation_size �o�C�g�Ń��[�e�[�V����<br>\n";
		print "    <table border=\"0\" cellpadding=\"0\"><tr>\n";
		print "      <td>�i�g�p�� $LogSizeRate%�j</td>\n";
		print "      <td>\n";
		print "        <table border=\"0\" width=\"$LogSizeGraphMaxLen\" cellpadding=\"0\"><tr><td CLASS=ListHeader2 align=\"left\">\n";
		print "          <table border=\"0\" width=\"$LogSizeGraphLen\" cellpadding=\"0\"><tr><td CLASS=ListHeader3>&nbsp;</td></tr></table>\n";
		print "        </td></tr></table>\n";
		print "      </td>\n";
		print "    </td></table>\n";
	} elsif($LOTATION eq '2') {
		print "�����ƂɃ��[�e�[�V����\n";
	} else {
		print "�����ƂɃ��[�e�[�V����\n";
	}
	print "  </TD>\n";
	print "</TR>\n";

	# ��̓��[�h���o��
	print "<TR>\n";
	print "  <TD BGCOLOR=\"#3A6EA5\" CLASS=ListHeader><B><FONT COLOR=\"#FFFFFF\">��̓��[�h</FONT></B></TD>\n";
	print "  <TD BGCOLOR=\"#EAEAEA\">\n";
	$tmp_year = substr($ana_month, 0, 4);
	$tmp_mon = substr($ana_month, 4, 2);
	if($mode eq 'DAILY') {
		print "���w�� $tmp_year�N $tmp_mon�� $ana_day��</TD>\n";
	} elsif($mode eq 'MONTHLY') {
		print "���w�� $tmp_year�N $tmp_mon��</TD>\n";
	} else {
		print "�S�w��\n";
	}
	print "</TR>\n";

	# ��̓��[�h�w�藓�o��
	print "<FORM ACTION=\"$CGI_URL\" METHOD=\"POST\">\n";
	print "<INPUT TYPE=\"hidden\" name=\"LOG\" value=\"$SelectedLogFileName\">\n";
	print "<TR>\n";
	print "  <TD BGCOLOR=\"#3A6EA5\" CLASS=ListHeader><B><FONT COLOR=\"#FFFFFF\">��̓��[�h�w��</FONT><B/></TD>\n";
	print "  <TD BGCOLOR=\"#EAEAEA\">\n";

	print "    <select name=\"MODE\">\n";
	if($mode ne 'DAILY' && $mode ne 'MONTHLY') {
		print "      <option value=\"\" selected>�S�w��</option>\n";
	} else {
		print "      <option value=\"\">�S�w��</option>\n";
	}
	if($mode eq 'MONTHLY') {
		print "      <option value=\"MONTHLY\" selected>���w��</option>\n";
	} else {
		print "      <option value=\"MONTHLY\">���w��</option>\n";
	}
	if($mode eq 'DAILY') {
		print "      <option value=\"DAILY\" selected>���w��</option>\n";
	} else {
		print "      <option value=\"DAILY\">���w��</option>\n";
	}
	print "    </select>\n";
	print '    <select name="MONTH">',"\n";
	my($y, $m);
	for $key (sort {$a <=> $b} keys(%year_mon_list)) {
		$y = substr($key, 0, 4);
		$m = substr($key, 4, 2);
		if($mode eq 'MONTHLY' && $key eq $ana_month) {
			print "      <option value=\"$key\" selected>$y�N $m��</option>\n";
		} else {
			print "      <option value=\"$key\">$y�N $m��</option>\n";
		}
	}
	print "    </select>\n";
	if($mode eq 'DAILY') {
		print "    <INPUT TYPE=\"TEXT\" NAME=\"DAY\" SIZE=\"2\" value=\"$ana_day\">��\n";
	} else {
		print "    <INPUT TYPE=\"TEXT\" NAME=\"DAY\" SIZE=\"2\">��\n";
	}
	print "    <INPUT TYPE=\"SUBMIT\" VALUE=\"��͊J�n\" NAME=\"ANALIZE\">\n";
	print "  </TD>\n";
	print "</TR>\n";
	print "</form>\n";

	# ��͑Ώۊ��ԗ��o��
	print "<TR>\n";
	print "  <TD BGCOLOR=\"#3A6EA5\" CLASS=ListHeader><B><FONT COLOR=\"#FFFFFF\">��͑Ώۊ���</FONT><B/></TD>\n";
	print "  <TD BGCOLOR=\"#EAEAEA\">$min_year/$min_mon/$min_mday $min_hour:$min_min:$min_sec �` $max_year/$max_mon/$max_mday $max_hour:$max_min:$max_sec</TD>\n";
	print "</TR>\n";
	print "</TABLE>\n";
	print "<BR>\n";
}

sub PrintLink {
	print "<HR>\n";
	if($ANA_REMOTETLD) {
		print '<A HREF="#COUNTRY">���ʃh���C�������|�[�g</A>';
	}
	if($ANA_REMOTEDOMAIN) {
		print ' | <A HREF="#DOMAIN">�A�N�Z�X���h���C�������|�[�g</A>';
	}
	if($ANA_REMOTEHOST) {
		print ' | <A HREF="#HOSTNAME">�A�N�Z�X���z�X�g�����|�[�g</A>';
	}
	if($ANA_HTTPLANG) {
		print ' | <A HREF="#LANGUAGE">�u���E�U�[�\���\���ꃌ�|�[�g</A>';
	}
	if($ANA_BROWSER) {
		print ' | <A HREF="#BROWSER">�u���E�U�[���|�[�g</A>';
	}
	if($ANA_PLATFORM) {
		print ' | <A HREF="#PLATFORM">�v���b�g�t�H�[�� ���|�[�g</A>';
	}
	if($ANA_REQUESTMONTHLY && $mode eq 'MONTHLY') {
		print ' | <A HREF="#DAILY">���t�ʃA�N�Z�X�����|�[�g</A>';
	}
	if($ANA_REQUESTDAILY && $mode eq '') {
		print ' | <A HREF="#MONTHLY">���ʃA�N�Z�X�����|�[�g</A>';
	}
	if($ANA_REQUESTHOURLY) {
		print ' | <A HREF="#HOURLY">���ԕʃA�N�Z�X�����|�[�g</A>';
	}
	if($ANA_REQUESTWEEKLY && $mode ne 'DAILY') {
		print ' | <A HREF="#WEEKLY">�j���ʃA�N�Z�X�����|�[�g</A>';
	}
	if($ANA_REQUESTFILE) {
		print ' | <A HREF="#REQUEST">���N�G�X�g���|�[�g</A>';
	}
	if($ANA_REFERERSITE) {
		print ' | <A HREF="#LINK_SITE">�����N���T�C�g���|�[�g</A>';
	}
	if($ANA_REFERERURL) {
		print ' | <A HREF="#LINK_URL">�����N��URL���|�[�g</A>';
	}
	if($ANA_KEYWORD) {
		print ' | <A HREF="#SEARCH_KEY">�����G���W���̌����L�[���[�h ���|�[�g</A>';
	}
	if($ANA_RESOLUTION) {
		print ' | <A HREF="#RESOLUTION">�N���C�A���g��ʉ𑜓x ���|�[�g</A>';
	}
	if($ANA_COLORDEPTH) {
		print ' | <A HREF="#COLORDEPTH">�N���C�A���g��ʐF�[�x ���|�[�g</A>';
	}
	if($ANA_VIDEOMEMORY) {
		print ' | <A HREF="#VIDEOMEMORY">�N���C�A���g�r�f�I�������[�T�C�Y ���|�[�g</A>'; 
	}
	print "<br><br>\n";
}


sub PrintRemoteTLD {
	# ���ʃh���C�������|�[�g
	print "<HR>\n";
	print '<A NAME="COUNTRY"><B class="size4">���ʃh���C�������|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">TLD</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";
	my $order = 1; 
	foreach $key (ValueSort(\%country_list)) {
		$rate = int($country_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$order</TD><TD>$key</TD><TD>$tld_list{$key}</TD><TD ALIGN=\"RIGHT\">$country_list{$key}</TD><TD class=\"size2\">";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";
		$order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}


sub PrintRemoteDomain {
	# �A�N�Z�X���h���C�������|�[�g
	print "<HR>\n";
	print '<A NAME="DOMAIN"><B class="size4">�A�N�Z�X���h���C�������|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�h���C����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";
	$order = 1;
	$dsp_order = 1;
	foreach $key (ValueSort(\%domain_list)) {
		unless($domain_list{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $ROW);
		}
		$rate = int($domain_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$dsp_order</TD><TD>$key</TD><TD ALIGN=\"RIGHT\">$domain_list{$key}</TD><TD class=\"size2\">\n";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		$pre_velue = $domain_list{$key};
		$order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}


sub PrintRomoteHost {
	# �A�N�Z�X���z�X�g�����|�[�g
	print "<HR>\n";
	print '<A NAME="HOSTNAME"><B class="size4">�A�N�Z�X���z�X�g�����|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�z�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";
	$order = 1;
	$dsp_order = 1;
	foreach $key (ValueSort(\%host_list)) {
		unless($host_list{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $ROW);
		}
		$rate = int($host_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		print "<TR BGCOLOR=\"#EAEAEA\"><TD><CENTER>$dsp_order</CENTER></TD><TD>$key</TD><TD ALIGN=\"RIGHT\">$host_list{$key}</TD><TD class=\"size2\">\n";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		$pre_velue = $host_list{$key};
		$order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}



sub PrintHttpLang {
	# �u���E�U�[�\���\���ꃌ�|�[�g
	print "<HR>\n";
	print '<A NAME="LANGUAGE"><B class="size4">�u���E�U�[�\���\���ꃌ�|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";
	my $lang_order = 1; 
	foreach $key (ValueSort(\%language_list)) {
		$rate = int($language_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$lang_order</TD><TD>";
		if($key eq '') {
			print "�s��";
		} else {
			print "$langcode_list{$key} ($key)";
		}
		print "</TD><TD ALIGN=\"RIGHT\">$language_list{$key}</TD><TD class=\"size2\">";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";
		$lang_order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}

sub PrintHttpUserAgentBrowser {
	# �u���E�U�[���|�[�g
	print "<HR>\n";
	print '<A NAME="BROWSER"><B class="size4">�u���E�U�[���|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�u���E�U�[</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";
	my $browser_order = 1;
	foreach $key (ValueSort(\%browser_list)) {
		$rate = int($browser_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		print "<TR BGCOLOR=\"#EAEAEA\" VALIGN=\"MIDDLE\"><TD ALIGN=\"CENTER\">$browser_order</TD><TD>";
		if($key eq '') {
			print " �s��</TD><TD ALIGN=\"RIGHT\">$browser_list{$key}</TD><TD>";
		} else {
			print " $key</TD><TD ALIGN=\"RIGHT\">$browser_list{$key}</TD><TD class=\"size2\">";
		}
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		for $key1 (sort(keys(%browser_v_list))) {
			if($key1 =~ /^$key:/) {
				$rate2 = int($browser_v_list{$key1} * 10000 / $loglines) / 100;
				$GraphLength2 = int($GRAPHMAXLENGTH * $rate2 / 100);
				$v = $key1;
				$v =~ s/^$key://;
				print "<TR class=\"size2\"><TD></TD><TD BGCOLOR=\"#B7B7B7\"><LI>$v</LI></TD><TD BGCOLOR=\"#B7B7B7\" ALIGN=\"RIGHT\">$browser_v_list{$key1}</TD>";
				print "<TD BGCOLOR=\"#B7B7B7\">";
				if($rate2 < 1) {
					print "\&nbsp\;";
				} else {
					print "<IMG SRC=\"$IMAGE_URL/graphbar2\.gif\" WIDTH=\"$GraphLength2\" HEIGHT=\"8\">";
				}
				print " ($rate2%)</TD></TR>\n";
			}
		}
		$browser_order ++;
	}
	print "</TABLE>\n";
	print "<BR><BR>\n";
}

sub PrintHttpUserAgentPlatform {
	# platform ���|�[�g
	print "<HR>\n";
	print '<A NAME="PLATFORM"><B class="size4">�v���b�g�t�H�[�� ���|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">Operating System</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";
	my $os_order = 1;
	foreach $key (ValueSort(\%platform_list)) {
		$rate = int($platform_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$os_order</TD><TD>";
		if($key eq '') {
			print " �s��</TD><TD ALIGN=\"RIGHT\">$platform_list{$key}</TD><TD>";
		} else {
			print " $key</TD><TD ALIGN=\"RIGHT\">$platform_list{$key}</TD><TD class=\"size2\">";
		}
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		for $key1 (sort(keys(%platform_v_list))) {
			if($key1 =~ /^$key:/) {
				$rate2 = int($platform_v_list{$key1} * 10000 / $loglines) / 100;
				$GraphLength2 = int($GRAPHMAXLENGTH * $rate2 / 100);
				$v = $key1;
				$v =~ s/^$key://;
				print "<TR class=\"size2\"><TD></TD><TD BGCOLOR=\"#B7B7B7\"><LI>$v</LI></TD><TD BGCOLOR=\"#B7B7B7\" ALIGN=\"RIGHT\">$platform_v_list{$key1}</TD>";
				print "<TD BGCOLOR=\"#B7B7B7\">";
				if($rate2 < 1) {
					print "\&nbsp\;";
				} else {
					print "<IMG SRC=\"$IMAGE_URL/graphbar2\.gif\" WIDTH=\"$GraphLength2\" HEIGHT=\"8\">";
				}
				print " ($rate2%)</TD></TR>\n";
			}
		}

		$os_order ++;
	}
	print "</TABLE>\n";
	print "<BR><BR>\n";
}

sub PrintRequestMonthly {
	print "<HR>\n";
	print '<A NAME="MONTHLY"><B class="size4">���ʃA�N�Z�X�����|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";
	for $key (sort keys %monthly_list) {
		$tmp_year = substr($key, 0, 4);
		$tmp_mon = substr($key, 4, 2);
		$rate = int($monthly_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		if($monthly_list{$key} > 0) {
			print "<TR BGCOLOR=\"#EAEAEA\"><TD><A HREF=\"$CGI_URL\?MODE=MONTHLY\&MONTH=$key\&LOG=$SelectedLogFileName\">$tmp_year�N $tmp_mon��</A>";
		} else {
			print "<TR BGCOLOR=\"#EAEAEA\"><TD>$tmp_year�N $tmp_mon��";
		}
		print "</TD><TD ALIGN=\"RIGHT\">$monthly_list{$key}</TD><TD class=\"size2\">";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";
		$key ++;
	}
	print "</TABLE>\n";
	print "<BR><BR>\n";
}

sub PrintRequestDaily {
	print "<HR>\n";
	print '<A NAME="DAILY"><B class="size4">���t�ʃA�N�Z�X�����|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���t</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";
	$key = 1;
	my($tmp_year) = substr($ana_month, 0, 4);
	my($tmp_mon) = substr($ana_month, 4, 2);
	my($last_day) = &LastDay($tmp_year, $tmp_mon);
	while($key <= $last_day) {
		if($key < 10) {
			$tmp_day = "0$key";
		} else {
			$tmp_day = $key;
		}
		$rate = int($date_list{"$tmp_year$tmp_mon$tmp_day"} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		$tmp_cnt = $date_list{"$tmp_year$tmp_mon$tmp_day"};
		$tmp_cnt = 0 if($date_list{"$tmp_year$tmp_mon$tmp_day"} eq '');
		$youbi = &Youbi($tmp_year, $tmp_mon, $key);
		if($tmp_cnt > 0) {
			print "<TR BGCOLOR=\"#EAEAEA\"><TD><A HREF=\"$CGI_URL\?MODE=DAILY\&MONTH=$ana_month\&DAY=$key&LOG=$SelectedLogFileName\">$tmp_year�N $tmp_mon�� $tmp_day��</A> (";
		} else {
			print "<TR BGCOLOR=\"#EAEAEA\"><TD>$tmp_year�N $tmp_mon�� $tmp_day�� (";
		}
		if($youbi == 0) {
			print "<FONT COLOR=\"RED\">$week_map[$youbi]</FONT>";
		} elsif($youbi == 6) {
			print "<FONT COLOR=\"BLUE\">$week_map[$youbi]</FONT>";
		} else {
			print "$week_map[$youbi]";
		}
		print ")</TD><TD ALIGN=\"RIGHT\">$tmp_cnt</TD><TD class=\"size2\">";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";
		$key ++;
	}
	print "</TABLE>\n";
	print "<BR><BR>\n";
}

sub PrintRequestHourly {
	# ���ԕʃA�N�Z�X�����|�[�g
	print "<HR>\n";
	print '<A NAME="HOURLY"><B class="size4">���ԕʃA�N�Z�X�����|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";
	$key = 0;
	until ($key ==24) {
		if($key < 10) {
			$key1 = "0$key";
		} else {
			$key1 = $key;
		}
		$rate = int($hourly_list{$key1} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		$hourly_list{$key1} = 0 if($hourly_list{$key1} eq '');
		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$key</TD><TD ALIGN=\"RIGHT\">$hourly_list{$key1}</TD><TD class=\"size2\">";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		$key ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}

sub PrintRequestWeekly {
	# �j���ʃA�N�Z�X�����|�[�g
	print "<HR>\n";
	print '<A NAME="WEEKLY"><B class="size4">�j���ʃA�N�Z�X�����|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�j��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";

	$key = 0;
	until($key == 7) {
		$rate = int($daily_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		$daily_list{$key} = 0 if($daily_list{$key} eq '');
		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$week_map[$key]</TD><TD ALIGN=\"RIGHT\">$daily_list{$key}</TD><TD class=\"size2\">\n";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";
		$key ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}


sub PrintRequestFile {
	# Request Report ��\��
	print "<HR>\n";
	print '<A NAME="REQUEST"><B class="size4">���N�G�X�g���|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�t�@�C��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";
	my($order) = 1;
	my($dsp_order) = 1;
	my($key, $HtmlTitle);
	foreach $key (ValueSort(\%request_list)) {
		unless($request_list{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $ROW);
		}
		$rate = int($request_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		$HtmlTitle = &GetHtmlTitle($key);
		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$dsp_order</TD><TD>";
		if($HtmlTitle) {
			print "$HtmlTitle";
		} else {
			print "<i>Page Has No Title</i>";
		}
		print "<br>";
		if($key eq '' || $key eq '-') {
			print "<div class=\"size2\">$key</div>";
		} else {
			print "<a href=\"$key\"><div class=\"size2\">$key</div></a>";
		}
		print "</TD><TD ALIGN=\"RIGHT\">$request_list{$key}</TD><TD class=\"size2\">\n";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		$pre_velue = $request_list{$key};
		$order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}


sub PrintRefererSite {
	# �����N���T�C�g
	print "<HR>\n";
	print '<A NAME="LINK_SITE"><B class="size4">�����N���T�C�g���|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�T�C�g</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";

	my($key, $dsp_url);
	my($order) = 1;
	my($dsp_order) = 1;
	my($refererSite_list) = ();
	my($url, $site, @url_parts, $Flag, $ExceptUrl);
	for $url (keys %referer_list) {
		$Flag = 0;
		if(scalar @MY_SITE_URLs) {
			for $ExceptUrl (@MY_SITE_URLs) {
				if($url =~ /^$ExceptUrl/) {
					$Flag = 1;
					last;
				}
			}
		}
		if($Flag) {next;}
		@url_parts = split(/\//, $url);
		$site = "$url_parts[0]//$url_parts[2]/";
		$refererSite_list{$site} += $referer_list{$url};
	}


	foreach $key (ValueSort(\%refererSite_list)) {
		unless($refererSite_list{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $ROW);
		}
		$rate = int($refererSite_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		if(length($key) > 50) {
			$dsp_url = substr($key, 0, 50);
			$dsp_url .= '...';
		} else {
			$dsp_url = $key;
		}
		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$dsp_order</TD><TD><A HREF=\"$key\">$dsp_url</A></TD><TD ALIGN=\"RIGHT\">$refererSite_list{$key}</TD><TD class=\"size2\">\n";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		$pre_velue = $refererSite_list{$key};
		$order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}


sub PrintRefererUrl {
	# �����N��URL
	print "<HR>\n";
	print '<A NAME="LINK_URL"><B class="size4">�����N��URL���|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">URL</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";

	my($key, $dsp_url, $ExceptUrl, $Flag);
	my($order) = 1;
	my($dsp_order) = 1;
	foreach $key (ValueSort(\%referer_list)) {
		$Flag = 0;
		if(scalar @MY_SITE_URLs) {
			for $ExceptUrl (@MY_SITE_URLs) {
				if($key =~ /^$ExceptUrl/) {
					$Flag = 1;
					last;
				}
			}
		}
		if($Flag) {next;}
		unless($referer_list{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $ROW);
		}
		$rate = int($referer_list{$key} * 10000 / $loglines) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		# �\������URL���A50�����ɏk�߂�
		if(length($key) > 50) {
			$dsp_url = substr($key, 0, 50);
			$dsp_url .= '...';
		} else {
			$dsp_url = $key;
		}

		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$dsp_order</TD><TD><A HREF=\"$key\">$dsp_url</A></TD><TD ALIGN=\"RIGHT\">$referer_list{$key}</TD><TD class=\"size2\">\n";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		$pre_velue = $referer_list{$key};
		$order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}


sub PrintKeyword {
	# �����G���W���̌����L�[���[�h��\������B
	print "<HR>\n";
	print '<A NAME="SEARCH_KEY"><B class="size4">�����G���W���̌����L�[���[�h ���|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�L�[���[�h</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";

	my($key, $dsp_url);
	my($order) = 1;
	my($dsp_order) = 1;
	my($cnt, $word);
	$cnt = 0;
	for $word (keys(%search_word)) {
		$cnt += $search_word{$word};
	}

	foreach $key (ValueSort(\%search_word)) {
		unless($search_word{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $ROW);
		}
		$rate = int($search_word{$key} * 10000 / $cnt) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$dsp_order</TD><TD>$key</TD><TD ALIGN=\"RIGHT\">$search_word{$key}</TD><TD class=\"size2\">\n";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		$pre_velue = $search_word{$key};
		$order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}


sub PrintResolution {
	# �𑜓x��\������B
	print "<HR>\n";
	print '<A NAME="RESOLUTION"><B class="size4">�N���C�A���g��ʉ𑜓x���|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�𑜓x</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";

	my($key, $dsp_url);
	my($order) = 1;
	my($dsp_order) = 1;
	my($cnt);
	$cnt = 0;
	for $key (keys(%ScreenResolution)) {
		$cnt += $ScreenResolution{$key};
	}

	foreach $key (ValueSort(\%ScreenResolution)) {
		unless($ScreenResolution{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $ROW);
		}
		$rate = int($ScreenResolution{$key} * 10000 / $cnt) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$dsp_order</TD><TD>$key</TD><TD ALIGN=\"RIGHT\">$ScreenResolution{$key}</TD><TD class=\"size2\">\n";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		$pre_velue = $ScreenResolution{$key};
		$order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";

}

sub PrintColorDepth {
	# �F�[�x��\������B
	print "<HR>\n";
	print '<A NAME="COLORDEPTH"><B class="size4">�N���C�A���g��ʐF�[�x ���|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�F�[�x</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";

	my($key);
	my($order) = 1;
	my($dsp_order) = 1;
	my($cnt);
	$cnt = 0;
	for $key (keys(%ScreenColorDepth)) {
		$cnt += $ScreenColorDepth{$key};
	}

	foreach $key (ValueSort(\%ScreenColorDepth)) {
		unless($ScreenColorDepth{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $ROW);
		}
		$rate = int($ScreenColorDepth{$key} * 10000 / $cnt) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);
		$ColorCount = 2 ** $key;
		$ColorCount = &CommaFormat($ColorCount);
		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$dsp_order</TD><TD>$ColorCount�F�i$key bit�j</TD><TD ALIGN=\"RIGHT\">$ScreenColorDepth{$key}</TD><TD class=\"size2\">\n";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		$pre_velue = $ScreenColorDepth{$key};
		$order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";

}


sub PrintVideoMemory {
	# �r�f�I�������[�T�C�Y��\������B
	print "<HR>\n";
	print '<A NAME="VIDEOMEMORY"><B class="size4">�N���C�A���g�r�f�I�������[�T�C�Y ���|�[�g</B></A>',"\n";
	print '<TABLE BORDER="0">',"\n";
	print '<TR BGCOLOR="#3A6EA5"><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">����</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�������[�T�C�Y</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">���N�G�X�g��</FONT></TH><TH CLASS=ListHeader><FONT COLOR="#FFFFFF">�O���t</FONT></TH></TR>',"\n";

	my($key);
	my($order) = 1;
	my($dsp_order) = 1;
	my($cnt);
	$cnt = 0;
	for $key (keys(%VideoMemory)) {
		$cnt += $VideoMemory{$key};
	}

	foreach $key (ValueSort(\%VideoMemory)) {
		unless($VideoMemory{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $ROW);
		}
		$rate = int($VideoMemory{$key} * 10000 / $cnt) / 100;
		$GraphLength = int($GRAPHMAXLENGTH * $rate / 100);

		print "<TR BGCOLOR=\"#EAEAEA\"><TD ALIGN=\"CENTER\">$dsp_order</TD><TD>$key MB</TD><TD ALIGN=\"RIGHT\">$VideoMemory{$key}</TD><TD class=\"size2\">\n";
		if($rate < 1) {
			print "";
		} else {
			print "<IMG SRC=\"$IMAGE_URL/graphbar\.gif\" WIDTH=\"$GraphLength\" HEIGHT=\"10\">";
		}
		print " ($rate%)</TD></TR>\n";

		$pre_velue = $VideoMemory{$key};
		$order ++;
	}
	print "</TABLE>\n";
	print "<br><br>\n";
}




# URL�G���R�[�h���ꂽ��������A�f�R�[�h���ĕԂ�
sub URL_Decode {
	my($str) = @_;
	$str =~ s/\+/ /g;
	$str =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C",hex($1))/eg;
	return $str;
}

# ����A���A���������Ɏ��A�j���R�[�h��Ԃ��B
# ��:0, ��:1, ��:2, ��:3, ��:4, ��:5, �y:6
sub Youbi {
	my($year, $month, $day) = @_;
	my($time) = timelocal(0, 0, 0, $day, $month - 1, $year);
	my(@date_array) = localtime($time);
	return $date_array[6];
}

# ����ƌ��������Ɏ��A�Y�����̍ŏI����Ԃ�
sub LastDay {
	my($year, $month) = @_;
	$month =~ s/^0//;
	if($month =~ /[^0-9]/ || $year =~ /[^0-9]/) {
		return '';
	}
	if($month < 1 && $month > 12) {
		return '';
	}
	if($year > 2037 || $year < 1900) {
		return '';
	}
	my($lastday) = 1;
	my($time) = timelocal(0, 0, 0, 1, $month-1, $year-1900);
	my(@date_array) = localtime($time);
	my($mon) = $date_array[4];
	my($flag) = 1;
	my($count) = 0;
	while($flag) {
		if($mon ne $date_array[4]) {
			return $lastday;
			$flag = 0;
		}
		$lastday = $date_array[3];
		$time = $time + (60 * 60 * 24);
		@date_array = localtime($time);
		$count ++;
		last if($count > 40);
	}
}


sub DateConv {
	my($day_time) = @_;
	my(@temp) = split(/ /, $day_time);
	$day_time = $temp[0];
	my($day, $hour, $min, $sec) = split(/:/, $day_time);
	my($mday, $mon, $year) = split(/\//, $day);

	%month = (
		'Jan'	=>	'01',
		'Feb'	=>	'02',
		'Mar'	=>	'03',
		'Apr'	=>	'04',
		'May'	=>	'05',
		'Jun'	=>	'06',
		'Jul'	=>	'07',
		'Aug'	=>	'08',
		'Sep'	=>	'09',
		'Oct'	=>	'10',
		'Nov'	=>	'11',
		'Dec'	=>	'12'
	);

	$mon = $month{$mon};
	return '' if($mon eq '');
	my($conv_time) = "$year$mon$mday$hour$min$sec";
	return $conv_time;

}

sub EncryptPasswd {
	my($pass) = @_;
	my @salt_set = ('a'..'z','A'..'Z','0'..'9','.','/');
	srand;
	my $seed1 = int(rand(64));
	my $seed2 = int(rand(64));
	my $salt = $salt_set[$seed1] . $salt_set[$seed2];
	return crypt($pass,$salt);
}

sub HtmlHeader {
	if($AUTHFLAG) {
		$CookieHeaderString = &SetCookie('PASS', $CRYPTED_PASS);
		print "$CookieHeaderString\n";
	}
	print "Content-type: text/html; charset=Shift_JIS\n";
	print "\n";
	open(HEAD, "./header.temp");
	my $line;
	while(<HEAD>) {
		$line = $_;
		$line =~ s/\$COPYRIGHT\$/$COPYRIGHT/g;
		print "$line";
	}
	close(HEAD);
}

sub HtmlFooter {
	open(FOOT, "./footer.temp");
	my $line;
	while(<FOOT>) {
		$line = $_;
		$line =~ s/\$COPYRIGHT\$/$COPYRIGHT/g;
		print "$line";
	}
	close(FOOT);
}

sub ErrorPrint {
	local($message) = @_;
	&HtmlHeader;
	print "<center>\n";
	print "$message\n";
	print "</center>\n";
	&HtmlFooter;
	exit;
}

sub InputCheck {
	if($mode eq 'DAILY') {
		if($ana_day =~ /[^0-9]/) {
			&ErrorPrint('���t�́A���p�����Ŏw�肵�Ă��������B');
		}
		$tmp_year = substr($ana_month, 0, 4);
		$tmp_mon = substr($ana_month, 4, 2);
		$last_day = &LastDay($tmp_year, $tmp_mon);
		if($ana_day > $last_day || $ana_day < 1) {
			&ErrorPrint('���t������������܂���B');
		}
	}
}

# �A�z�z���l�ivalue�j�Ń\�[�g�����A�z�z���Ԃ�
sub ValueSort {
	my $x = shift;
	my %array=%$x;
	return sort {$array{$b} <=> $array{$a};} keys %array;
}

# �w�肳�ꂽ��`�t�@�C����ǂݎ��A�A�z�z���Ԃ��B
sub ReadDef {
	my($file) = @_;
	my(@buff, %array);
	open(FILE, "$file") || &ErrorPrint("$file ���I�[�v���ł��܂���ł����B");
	while(<FILE>) {
		chop;
		@buff = split(/=/);
		$array{$buff[0]} = $buff[1];
	}
	close(FILE);
	return %array;
}


sub Auth {
	my($in_crypted_pass) = @_;
	my $salt;
	if($in_crypted_pass =~ /^\$1\$([^\$]+)\$/) {
		#MD5�̏ꍇ
		$salt = $1;
	} else {
		#DES�̏ꍇ
		$salt = substr($in_crypted_pass, 0, 2);
	}
	my $crypted_pass = crypt($PASSWORD, $salt);
	if($crypted_pass eq $in_crypted_pass) {
		return 1;
	} else {
		return 0;
	}
}

sub PrintAuthForm {
	my($Repeat) = @_;
	print "Content-type: text/html; charset=Shift_JIS\n\n";
	print '<html>
<head>
<meta http-equiv="content-type" content="text/html;charset=shift_jis">
<title>futomi\'s CGI Cafe - ���@�\�A�N�Z�X���CGI Standard��</title>
<style type="text/css">
  table  { font-size: 12px; }
  a  { font-size: 12px; }
  div { font-size: 12px; }
</style>
</head>

<body bgcolor="#ffffff">
';
	if($Repeat) {
		print "<div style=\"color:#FF0000\">�p�X���[�h���Ⴂ�܂��B</div>\n";
	}
	print "<form action=\"${$CGI_URL}\" method=\"post\">\n";
	print '<table border="0" cellspacing="2" cellpadding="2">
<tr>
<td nowrap>�p�X���[�h</td>
<td nowrap><input type="password" name="PASS" size="24"></td>
<td nowrap><input type="submit" name="auth_button" value="�@�F�@�؁@"></td>
</tr>
</table>
</form>
<hr>
<div><a href="http://www.futomi.com/" target="_blank">futomi\'s CGI Cafe - ���@�\�A�N�Z�X���CGI Standard��</a></div>
</body>
</html>
';
	exit;
}


sub SetCookie {
	my($CookieName, $CookieValue) = @_;
	# URL�G���R�[�h
	$CookieValue =~ s/([^\w\=\& ])/'%' . unpack("H2", $1)/eg;
	$CookieValue =~ tr/ /+/;
	my($CookieHeaderString) = "Set-Cookie: $CookieName=$CookieValue\;";
	return $CookieHeaderString;
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


sub GetSelectedLogFile {
	my $LogDir = $LOG;
	$LogDir =~ s/\/([^\/]*)$//;
	my $LogFileName = $1;
	my $SelectedLogFileName = $query->param('LOG');
	unless($SelectedLogFileName) {
		if($LOTATION == 2) {
			my $DateStr = &GetToday;
			$SelectedLogFileName = "$LogFileName\.$DateStr\.cgi";
		} elsif($LOTATION == 3) {
			my $DateStr = &GetToday;
			my $MonStr = substr($DateStr, 0, 6);
			$SelectedLogFileName = "$LogFileName\.$MonStr"."00.cgi";
		} else {
			$SelectedLogFileName = "$LogFileName\.cgi";
		}
	}
	my $SelectedLogFile = "$LogDir/$SelectedLogFileName";
	return($SelectedLogFile, $SelectedLogFileName);
}


sub GetPastLogList {
	my %LogList = ();
	my $LogDir = $LOG;
	$LogDir =~ s/\/([^\/]*)$//;
	my $LogFileName = $1;
	unless($LogDir) {$LogDir = '.';}
	opendir(LOGDIR, "$LogDir") || &ErrorPrint("���O�i�[�f�B���N�g���u$LogDir�v���I�[�v���ł��܂���ł����B");
	my @FileList = readdir(LOGDIR);
	for $key (@FileList) {
		if($key =~ /^$LogFileName/) {
			$LogList{$key} = "$LogDir\/$key";
		}
	}
	return %LogList;
}


sub GetToday {
	my(@Date) = localtime(time + $TIMEDIFF*60*60);
	my($Year) = $Date[5] + 1900;
	my($Mon) = $Date[4] + 1;
	my($Day) = $Date[3];
	if($Mon < 10) {$Mon = "0$Mon";}
	if($Day < 10) {$Day = "0$Day";}
	return $Year.$Mon.$Day;
}


#�w�肵���h�L�������g���[�g����̃p�X����A�^�C�g�����擾����B
sub GetHtmlTitle {
	my($URL) = @_;
	$URL =~ s/\?.*$//;
	$URL =~ s/\#.*$//;
	my($Title, $Path, $HtmlFile);
	if($URL2PATH_FLAG) {
		for my $key (keys %URL2PATH) {
			if($URL =~ /^$key/) {
				$HtmlFile = $URL;
				$HtmlFile =~ s/^$key/$URL2PATH{$key}/;
			}
		}
		unless($HtmlFile) {
			return '';
		}
	} else {
		$_ = $URL;
		m|https*://[^/]+/(.*)|;
		$Path = '/'.$1;
		$HtmlFile = $ENV{'DOCUMENT_ROOT'}.$Path;
	}
	unless(-e $HtmlFile) {return ''};
	open(HTML, "$HtmlFile") || return '';
	my $HitFlag  = 0;
	while(<HTML>) {
		chop;
		$LineString = $_;
		if( $LineString =~ /<title>([^<]*)<\/title>/i ) {
			$Title = $1;
			$HitFlag = 1;
			last;
		}
		if( $LineString =~ /<\/head>/i ) {last;}

	}
	close(HTML);
	if($HitFlag) {
		&jcode::convert(\$Title, "sjis");
		return $Title;
	} else {
		return '';
	}
}


sub GetCgiUrl {
	return "acc.cgi";
}

sub CommaFormat {
	my($num) = @_;
	#�����ƃh�b�g�ȊO�̕������܂܂�Ă�����A���������̂܂ܕԂ��B
	if($num =~ /[^0-9\.]/) {return $num;}
	#���������Ə����_�𕪗�
	my($int, $decimal) = split(/\./, $num);
	#���������̌����𒲂ׂ�
	my $figure = length $int;
	my $commaformat;
	#���������ɃJ���}��}��
	for(my $i=1;$i<=$figure;$i++) {
		my $n = substr($int, $figure-$i, 1);
		if(($i-1) % 3 == 0 && $i != 1) {
			$commaformat = "$n,$commaformat";
		} else {
			$commaformat = "$n$commaformat";
		}
	}
	#�����_������΁A�����������
	if($decimal) {
		$commaformat .= "\.$decimal";
	}
	#���ʂ�Ԃ�
	return $commaformat;
}

sub User_Agent {
	my($user_agent, $remote_host) = @_;
	my($platform, @agentPart, $browser, $browser_v);
	my($platform_v, @agentPart2, $user_agent2, @buff, @buff2, @buff3);
	my($flag, $key, @version_buff);

	if($user_agent =~ /DoCoMo/i) {
		$platform = 'DoCoMo';
		@agentPart = split(/\//, $user_agent);
		$browser = 'DoCoMo';
		$browser_v = $agentPart[1];
		$platform_v = $agentPart[2];
		if($platform_v eq '') {
			if($user_agent =~ /DoCoMo\/([0-9\.]+)\s+([0-9a-zA-Z]+)/) {
				$browser_v = $1;
				$platform_v = $2;
			}
		}
	} elsif($user_agent =~ /NetPositive/i) {
		$browser = 'NetPositive';
		if($user_agent =~ /NetPositive\/([0-9\.\-]+)/) {
			$browser_v = $1;
		}
		$platform = 'BeOS';
		$platform_v = '';
	} elsif($user_agent =~ /OmniWeb/) {
		$browser = 'OmniWeb';
		if($user_agent =~ /Mac_PowerPC/i) {
			$platform = 'MacOS';
			$platform_v = 'PowerPC';
		} else {
			$platform = '';
			$platform_v = '';
		}
		if($user_agent =~ /OmniWeb\/([0-9\.]+)/) {
			$browser_v = $1;
		} else {
			$browser_v = '';
		}
	} elsif($user_agent =~ /Cuam/i) {
		$browser = 'Cuam';
		$platform = 'Windows';
		$browser_v = '';
		$platform_v = '';
		if($user_agent =~ /Cuam Ver([0-9\.]+)/i) {
			$platform_v = '';
			$browser_v = $1;
		} else {
			if($user_agent =~ /Windows\s+([^\;\)]+)/) {
				$platform_v = $1;
			}
			if($user_agent =~ /Cuam\s+(0-9a-z\.)/) {
				$browser_v = $1;
			}
		}
	} elsif($user_agent =~ /^JustView\/([0-9\.]+)/) {
		$platform = 'Windows';
		$platform_v = '';
		$browser = 'JustView';
		$browser_v = $1;
	} elsif($user_agent =~ /^sharp pda browser\/([0-9\.]+).*\((.+)\//) {
		$platform = 'ZAURUS';
		$platform_v = $2;
		$browser = 'sharp_pda_browser';
		$browser_v = $1;
	} elsif($user_agent =~ /DreamPassport\/([0-9\.]+)/) {
		$platform = 'Dreamcast';
		$platform_v = '';
		$browser = 'DreamPassport';
		$browser_v = $1;
	} elsif($user_agent =~ /^Sonybrowser2 \(.+\/PlayStation2 .+\)/) {
		$platform = 'PlayStation2';
		$platform_v = '';
		$browser = 'Sonybrowser2';
		$browser_v = '';
	} elsif($user_agent =~ /(CBBoard|CBBstandard)\-[0-9\.]+/) {
		$platform = 'DoCoMo';
		$platform_v = 'ColorBrowserBorad';
		$browser = 'DoCoMo';
		$browser_v = 'ColorBrowserBorad';
	} elsif($user_agent =~ /^PDXGW/) {
		$platform = 'DDI POCKET';
		$platform_v = 'H"';
		$browser = 'DDI POCKET';
		$browser_v = 'H"';
	} elsif($user_agent =~ /^Sleipnir Version ([0-9\.]+)/) {
		$browser = 'Sleipnir';
		$browser_v = $1;
		$platform = 'Windows';
		$platform_v = '';
	} elsif($user_agent =~ /Safari\/([0-9]+)/) {
		$browser = 'Safari';
		$browser_v = $1;
		$platform = 'MacOS';
		if($user_agent =~ / PPC /) {
			$platform_v = 'PowerPC';
		}
	} elsif($user_agent =~ /UP\.\s*Browser/i) {
		$user_agent =~ s/UP\.\s*Browser/UP\.Browser/;
		$browser = 'UP.Browser';
		@agentPart = split(/ /, $user_agent);
		if($agentPart[0] =~ /KDDI/i) {
			my @tmp = split(/\-/, $agentPart[0]);
			$platform_v = $tmp[1];
			my @tmp2 = split(/\//, $agentPart[1]);
			$browser_v = $tmp2[1];
		} else {
			@agentPart2 = split(/\//, $agentPart[0]);
			($browser_v, $platform_v) = split(/\-/, $agentPart2[1]);
		}
		my %devid_list = (
			'P-PAT'=>'DoCoMo,P-PAT',
			'D2'=>'DoCoMo,D2',
			'SA31' => 'au,W21SA',
			'KC32' => 'au,W21K',
			'KC31' => 'au,W11K',
			'SN31' => 'au,W21S',
			'HI32' => 'au,W21H',
			'HI31' => 'au,W11H',
			'ST22' => 'au,INFOBAR',
			'SA27' => 'au,A5505SA',
			'SA26' => 'au,A5503SA',
			'TS26' => 'au,A5501T',
			'CA25' => 'au,A5406CA',
			'SN25' => 'au,A5404S',
			'SN24' => 'au,A5402S',
			'CA23' => 'au,A5401CA',
			'KC22' => 'au,A5305K',
			'HI24' => 'au,A5303H II',
			'CA22' => 'au,A5302CA',
			'TS21' => 'au,C5001T',
			'TS28' => 'au,A5506T',
			'TS27' => 'au,A5504T',
			'KC24' => 'au,A5502K',
			'KC25' => 'au,A5502K',
			'CA26' => 'au,A5407CA',
			'ST23' => 'au,A5405SA',
			'CA24' => 'au,A5403CA',
			'CA23' => 'au,A5401CA II',
			'ST21' => 'au,A5306ST',
			'TS24' => 'au,A5304T',
			'HI23' => 'au,A5303H',
			'TS23' => 'au,A5301T',
			'SN27' => 'au,A1402S II',
			'SN26' => 'au,A1402S',
			'SA28' => 'au,A1305SA',
			'TS25' => 'au,A1304T',
			'SA24' => 'au,A1302SA',
			'SN22' => 'au,A1101S',
			'SN28' => 'au,A1402S II',
			'KC23' => 'au,A1401K',
			'TS25' => 'au,A1304T II',
			'SA25' => 'au,A1303SA',
			'SN23' => 'au,A1301S',
			'SA22' => 'au,A3015SA',
			'TS22' => 'au,A3013T',
			'SA21' => 'au,A3011SA',
			'KC21' => 'au,C3002K',
			'SN21' => 'au,A3014S',
			'CA21' => 'au,A3012CA',
			'MA21' => 'au,C3003P',
			'HI21' => 'au,C3001H',
			'ST14' => 'au,A1014ST',
			'KC14' => 'au,A1012K',
			'SN17' => 'au,C1002S',
			'CA14' => 'au,C452CA',
			'TS14' => 'au,C415T',
			'SN15' => 'au,C413S',
			'SN16' => 'au,C413S',
			'ST12' => 'au,C411ST',
			'CA13' => 'au,C409CA',
			'HI13' => 'au,C407H',
			'SY13' => 'au,C405SA',
			'ST11' => 'au,C403ST',
			'SY12' => 'au,C401SA',
			'CA12' => 'au,C311CA',
			'HI12' => 'au,C309H',
			'KC11' => 'au,C307K',
			'SY11' => 'au,C304SA',
			'HI11' => 'au,C302H',
			'DN01' => 'au,C202DE',
			'KC15' => 'au,A1013K',
			'ST13' => 'au,A1011ST',
			'SY15' => 'au,C1001SA',
			'HI14' => 'au,C451H',
			'KC13' => 'au,C414K',
			'SY14' => 'au,C412SA',
			'TS13' => 'au,C410T',
			'MA13' => 'au,C408P',
			'SN13' => 'au,C406S',
			'SN12' => 'au,C404S',
			'SN14' => 'au,C404S',
			'DN11' => 'au,C402DE',
			'KC12' => 'au,C313K',
			'TS12' => 'au,C310T',
			'MA11' => 'au,C308P',
			'MA12' => 'au,C308P',
			'SN11' => 'au,C305S',
			'CA11' => 'au,C303CA',
			'TS11' => 'au,C301T',
			'HI01' => 'au,C201H',
			'HI02' => 'au,C201H',
			'KCU1' => 'TU-KA,TK41',
			'KCTD' => 'TU-KA,TK40',
			'TST7' => 'TU-KA,TT31',
			'SYT4' => 'TU-KA,TS31',
			'KCTA' => 'TU-KA,TK22',
			'KCT9' => 'TU-KA,TK21',
			'TST4' => 'TU-KA,TT11',
			'SYT3' => 'TU-KA,TS11',
			'MIT1' => 'TU-KA,TD11',
			'KCT6' => 'TU-KA,TK05',
			'KCT5' => 'TU-KA,TK04',
			'SYT2' => 'TU-KA,TS02',
			'TST2' => 'TU-KA,TT02',
			'KCT1' => 'TU-KA,TK01',
			'SYT1' => 'TU-KA,TSO1',
			'SYT5' => 'TU-KA,TS41',
			'TST8' => 'TU-KA,TT32',
			'KCTC' => 'TU-KA,TK31',
			'KCTB' => 'TU-KA,TK23',
			'TST6' => 'TU-KA,TT22',
			'TST5' => 'TU-KA,TT21',
			'KCT8' => 'TU-KA,TK12',
			'KCT7' => 'TU-KA,TK11',
			'MAT3' => 'TU-KA,TP11',
			'TST3' => 'TU-KA,TT03',
			'KCT4' => 'TU-KA,TK03',
			'MAT1' => 'TU-KA,TP01',
			'MAT2' => 'TU-KA,TP01',
			'KCT2' => 'TU-KA,TK02',
			'KCT3' => 'TU-KA,TK02',
			'TST1' => 'TU-KA,TT01',
			'NT95'=>'UP.SDK',
			'UPG'=>'UP.SDK'
		);
		if($devid_list{$platform_v} eq '') {
			$platform = '';
			$platform_v = '';
		} else {
			($platform, $platform_v) = split(/,/, $devid_list{$platform_v});
		}
	} elsif($user_agent =~ /^J-PHONE/) {
		$platform = 'vodafone';
		$browser = 'vodafone';
		my @parts = split(/\//, $user_agent);
		$browser_v = $parts[1];
		$platform_v = $parts[2];
	} elsif($user_agent =~ /^ASTEL\/(.+)\/(.+)\/(.+)\//) {
		$platform = 'ASTEL';
		$browser = 'ASTEL';
		$browser_v = '';
		$platform_v = substr($2, 0, 5);
	} elsif($user_agent =~ /^Mozilla\/.+ AVE-Front\/(.+) \(.+\;Product=(.+)\;.+\)/) {
		$browser = 'NetFront';
		$browser_v = $1;
		$platform = $2;
		$platform_v = '';
	} elsif($user_agent =~ /^Mozilla\/.+ Foliage-iBrowser\/([0-9\.]+) \(WinCE\)/) {
		$platform = 'Windows';
		$platform_v = 'CE';
		$browser = 'Foliage-iBrowser';
		$browser_v = $1;		
	} elsif($user_agent =~ /^Mozilla\/.+\(compatible\; MSPIE ([0-9\.]+)\; Windows CE/) {
		$platform = 'Windows';
		$platform_v = 'CE';
		$browser = 'PocketIE';
		$browser_v = $1;
	} elsif($user_agent =~ /Opera/) {
		$browser = "Opera";
		if($user_agent =~ /^Opera\/([0-9\.]+)/) {
			$browser_v = $1;
		} elsif($user_agent =~ /Opera\s+([0-9\.]+)/) {
			$browser_v = $1;
		} else {
			$browser_v = '';
		}
		if($user_agent =~ /Windows\s+([^\;]+)(\;|\))/i) {
			$platform = "Windows";
			$platform_v = $1;
			if($platform_v eq 'NT 5.0') {
				$platform_v = '2000';
			} elsif($platform_v eq 'NT 5.1') {
				$platform_v = 'XP';
			} elsif($platform_v eq 'ME') {
				$platform_v = 'Me';
			}
		} elsif($user_agent =~ /Macintosh\;[^\;]+\;([^\)]+)\)/) {
			$platform = "MacOS";
			$platform_v = $1;
			if($platform_v eq 'PPC') {
				$platform_v = 'PowerPC';
			}
		} elsif($user_agent =~ /Mac_PowerPC/i) {
			$platform = 'MacOS';
			$platform_v = 'PowerPC';
		} elsif($user_agent =~ /Linux\s+([0-9\.\-]+)/) {
			$platform = "Linux";
			$platform_v = $1;
		} elsif($user_agent =~ /BeOS ([A-Z0-9\.\-]+)(\;|\))/) {
			$platform = 'BeOS';
			$platform_v = $1;
		} else {
			$platform = '';
			$platform_v = '';
		}
	} elsif($user_agent =~ /^Mozilla\/[^\(]+\(compatible\; MSIE .+\)/) {
		if($user_agent =~ /NetCaptor ([0-9\.]+)/) {
			$browser = 'NetCaptor';
			$browser_v = $1;
		} else {
			$browser = 'InternetExplorer';
			$user_agent2 = $user_agent;
			$user_agent2 =~ s/ //g;
			@buff = split(/\;/, $user_agent2);
			@version_buff = grep(/MSIE/i, @buff);
			$browser_v = $version_buff[0];
			$browser_v =~ s/MSIE//g;
			if($browser_v =~ /^([0-9]+)\.([0-9]+)/) {
        			$browser_v = "$1\.$2";
			}
		}

		if($user_agent =~ /Windows 3\.1/i) {
			$platform = 'Windows';
			$platform_v = '3.1';
		} elsif($user_agent =~ /Win32/i) {
			$platform = 'Windows';
			$platform_v = '32';
		} elsif($user_agent =~ /Windows 95/i) {
			$platform = 'Windows';
			$platform_v = '95';
		} elsif($user_agent =~ /Windows 98/i) {
			$platform = 'Windows';
			if($user_agent =~ /Win 9x 4\.90/) {
				$platform_v = 'Me';
			} else {
				$platform_v = '98';
			}
		} elsif($user_agent =~ /Windows NT 5\.0/i) {
			$platform = 'Windows';
			$platform_v = '2000';
		} elsif($user_agent =~ /Windows NT 5\.1/i) {
			$platform = 'Windows';
			$platform_v = 'XP';
		} elsif($user_agent =~ /Windows NT/i 
				&& $user_agent !~ /Windows NT 5\.0/i) {
			$platform = 'Windows';
			$platform_v = 'NT';
		} elsif($user_agent =~ /Windows 2000/) {
			$platform = 'Windows';
			$platform_v = '2000';
		} elsif($user_agent =~ /Windows ME/i) {
			$platform = 'Windows';
			$platform_v = 'Me';
		} elsif($user_agent =~ /Windows XP/i) {
			$platform = 'Windows';
			$platform_v = 'XP';
		} elsif($user_agent =~ /Windows CE/i) {
			$platform = 'Windows';
			$platform_v = 'CE';
		} elsif($user_agent =~ /Mac/i) {
			$platform = 'MacOS';
			if($user_agent =~ /Mac_68000/i) {
				$platform_v = '68K';
			} elsif($user_agent =~ /Mac_PowerPC/i) {
				$platform_v = 'PowerPC';
			}
		} elsif($user_agent =~ /WebTV/i) {
			$platform = 'WebTV';
			@buff2 = split(/ /, $user_agent);
			@buff3 = split(/\//, $buff2[1]);
			$platform_v = $buff3[1];
		} else {
			$platform = '';
			$platform_v = '';
		}
	} elsif($user_agent =~ /^Mozilla\/([0-9\.]+)/) {
		$browser = 'NetscapeNavigator';
		$browser_v = $1;
		if($user_agent =~ /Gecko\//) {
			if($user_agent =~ /Netscape[0-9]*\/([0-9a-zA-Z\.]+)/) {
				$browser_v = $1;
			} elsif($user_agent =~ /(Phoenix|Chimera|Firefox|Camino)\/([0-9a-zA-Z\.]+)/) {
				$browser = $1;
				$browser_v = $2;
			} else {
				$browser = 'Mozilla';
				if($user_agent =~ /rv:([0-9\.]+)/) {
					$browser_v = $1;
				} else {
					$browser_v = '';
				}
			}
		}

		if($user_agent =~ /Win95/) {
			$platform = 'Windows';
			$platform_v = '95';
		} elsif($user_agent =~ /Windows 95/) {
			$platform = 'Windows';
			$platform_v = '95';
		} elsif($user_agent =~ /Win 9x 4\.90/i) {
			$platform = 'Windows';
			$platform_v = 'Me';
		} elsif($user_agent =~ /Windows Me/i) {
			$platform = 'Windows';
			$platform_v = 'Me';
		} elsif($user_agent =~ /Win98/i) {
			$platform = 'Windows';
			$platform_v = '98';
		} elsif($user_agent =~ /WinNT/i) {
			$platform = 'Windows';
			$platform_v = 'NT';
		} elsif($user_agent =~ /Windows NT 5\.0/i) {
			$platform = 'Windows';
			$platform_v = '2000';
		} elsif($user_agent =~ /Windows NT 5\.1/i) {
			$platform = 'Windows';
			$platform_v = 'XP';
		} elsif($user_agent =~ /Windows 2000/i) {
			$platform = 'Windows';
			$platform_v = '2000';
		} elsif($user_agent =~ /Windows XP/i) {
			$platform = 'Windows';
			$platform_v = 'XP';
		} elsif($user_agent =~ /Macintosh/i) {
			$platform = 'MacOS';
			if($user_agent =~ /68K/i) {
				$platform_v = '68K';
			} elsif($user_agent =~ /PPC/i) {
				$platform_v = 'PowerPC';
			}
		} elsif($user_agent =~ /SunOS/i) {
			$platform = 'SunOS';
			if($user_agent =~ /SunOS\s+([0-9\-\.]+)/i) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /Linux/i) {
			$platform = 'Linux';
			if($user_agent =~ /Linux\s+([0-9\-\.]+)/) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /FreeBSD/i) {
			$platform = 'FreeBSD';
			if($user_agent =~ /FreeBSD\s+([a-zA-Z0-9\.\-\_]+)/i) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /NetBSD/i) {
			$platform = 'NetBSD';
			$platform_v = '';
		} elsif($user_agent =~ /AIX/i) {
			$platform = 'AIX';
			if($user_agent =~ /AIX\s+([0-9\.]+)/) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /IRIX/i) {
			$platform = 'IRIX';
			if($user_agent =~ /IRIX\s+([0-9\.]+)/i) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /HP-UX/i) {
			$platform = 'HP-UX';
			if($user_agent =~ /HP-UX\s+([a-zA-Z0-9\.]+)/i) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /OSF1/i) {
			$platform = 'OSF1';
			if($user_agent =~ /OSF1\s+([a-zA-Z0-9\.]+)/i) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /BeOS/i) {
			$platform = 'BeOS';
			$platform_v = '';
		} else {
			$platform = '';
			$platform_v = '';
		}
	} else {
		$platform = '';
		$platform_v = '';
		$browser = '';
		$browser_v = '';
	}

	return ($platform, $platform_v, $browser, $browser_v);

}
