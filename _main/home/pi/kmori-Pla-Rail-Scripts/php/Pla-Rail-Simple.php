<?php
$action = $_GET["action"];

$host="127.0.0.1";
$port=10501;

if( strlen($action) > 0 ) 
{
	if( ($sock = socket_create(AF_INET,SOCK_STREAM,0)) < 0 )
	{
		exit("socket failure. Can't create a socket!");
	};

	if( !socket_connect ( $sock , $host , $port) )
	{
		exit("connect failure. Maybe no server is running");
	};

	if( !socket_send ( $sock , $action , strlen($action), MSG_EOF) )
	{
		exit("send failure. Maybe server restart is required!");
	};

	socket_close ( $sock );
};

?>
<p><a href="/Pla-Rail-Simple.php?action=GO_">Go!!</a></p>
<p>&nbsp;</p>
<p><a href="/Pla-Rail-Simple.php?action=STOP_">Stop!!</a></p>
<p>&nbsp;</p>
