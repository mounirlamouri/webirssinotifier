use strict;
use warnings;

use Irssi;
use URI::Escape;
use vars qw($VERSION %IRSSI); 

our $VERSION = "0.8";
our %IRSSI = (
  authors     => 'Mounir Lamouri',
  contact     => 'mounir@lamouri.fr',
  name        => "webirssinotifier",
  description => "Notify of IRC pings via push messages in your browser.",
  license     => "Apache-2.0",
  url         => "https://github.com/mounirlamouri/webirssinotifier/",
);

# Users must set webirssinotifier_user to the user that should receive the push
# notifications.
# /set webirssinotifier_user <USER>

# Users can use webirssinotifier_away_only to only get push notifications when
# they are away:
# /set webirssinotifier_away_only on

# Users can use webirssinotifier_idle_time to only get push notifications when
# they have been inactive for longer than X seconds.
# /set webirssinotifier_idle_time X

our $keyPressedTimestamp = time;

sub should_send_message {
  my ($server) = @_;

  if (Irssi::settings_get_bool('webirssinotifier_away_only') &&
      !$server->{usermode_away}) {
    return 0;
  }

  return Irssi::settings_get_int('webirssinotifier_idle_time') < (time - $keyPressedTimestamp);
}

sub send_message {
  my ($type, $name, $body) = @_;

  my $user = Irssi::settings_get_str('webirssinotifier_user');
  `curl --silent --header "Content-Type: application/json" https://webirssinotifier.appspot.com/send -d "{\\"user\\": \\"${user}\\", \\"type\\": \\"$type\\", \\"name\\": \\"${name}\\", \\"body\\": \\"${body}\\"}" > /dev/null 2>&1 `;
}

sub signal_print_text {
  my ($dest, $text, $stripped) = @_;

  if ((($dest->{level} & MSGLEVEL_PUBLIC) == 0) ||
      (($dest->{level} & MSGLEVEL_NOHILIGHT) != 0) ||
      (($dest->{level} & MSGLEVEL_HILIGHT) == 0)) {
    return;
  }   

  if (should_send_message($dest->{server})) {
    send_message("channel", $dest->{target}, uri_escape(Irssi::strip_codes($text)));
  }
}

sub signal_message_private {
  my ($server, $msg, $nick, $address) = @_;

  if (should_send_message($server)) {
    send_message("query", $nick, uri_escape(Irssi::strip_codes($msg)));
  }
}

sub signal_key_pressed {
  $keyPressedTimestamp = time;
}

sub signal_setup_changed {
  Irssi::signal_remove('gui key pressed', 'signal_key_pressed');
  if (Irssi::settings_get_int('webirssinotifier_idle_time') > 0) {
    Irssi::signal_add('gui key pressed', 'signal_key_pressed');
  }
}

Irssi::settings_add_str('webirssinotifier', 'webirssinotifier_user', '');
Irssi::settings_add_int('irssinotifier', 'webirssinotifier_idle_time', 0);
Irssi::settings_add_bool('webirssinotifier', 'webirssinotifier_away_only', 0);

Irssi::signal_add('print text', 'signal_print_text');
Irssi::signal_add('message private', 'signal_message_private');
Irssi::signal_add('setup changed', 'signal_setup_changed');
