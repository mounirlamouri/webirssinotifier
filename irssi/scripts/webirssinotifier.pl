# Notify of public and private pings via push messages.

use Irssi;
use vars qw($VERSION %IRSSI);

$VERSION = "0.0";
%IRSSI = (
  authors     => 'Mounir Lamouri <mounir@lamouri.fr>',
  name        => "webirssinotifier",
  description => "Notify of public and private pings via push messages.",
  license     => "Apache v2.0",
  url         => "https://github.com/mounirlamouri/webirssinotifier/",
);

$USER = "email\@address";

# TODO:
# * Have an option to only send push if the user is away on the server.
# * Show nicks, probably by tracking 'private' signal.

sub signal_print_text {
  my ($dest, $text, $stripped) = @_;
  my $opt = MSGLEVEL_HILIGHT|MSGLEVEL_MSGS;
  my $channel = '';

  if (($dest->{level} & ($opt)) &&
      ($dest->{level} & MSGLEVEL_NOHILIGHT) == 0) {
    if ($dest->{level} & MSGLEVEL_PUBLIC) {
      $channel = $dest->{target};
    }

    $text = Irssi::strip_codes($text);
    $result = `curl --silent --header "Content-Type: application/json" https://webirssinotifier.appspot.com/send -d "{\\"user\\": \\"${USER}\\", \\"channel\\": \\"${channel}\\", \\"text\\": \\"${text}\\"}" > /dev/null 2>&1 `;
  }
}

#sub signal_message_private {
#  my ($msg, $nick, $address) = @_;
#
#  $msg = Irssi::strip_codes($msg);
#  $result = `curl --silent --header "Content-Type: application/json" https://webirssinotifier.appspot.com/send -d "{\\"user\\": \\"${USER}\\", \\"channel\\": \\"\\", \\"nick\\": \\"${nick}\\", \\"text\\": \\"${msg}\\"}" > /dev/null 2>&1 `;
#}

Irssi::signal_add('print text', 'signal_print_text');
#Irssi::signal_add('message private', 'signal_message_private');
