# Text-based LAN Multiplayer game
Role-playing LAN multiplayer game developed in Python3 as a college project.
<h1 align="center">INSTRUCTIONS</h1>
To start playing, you must run the server (server.py) and then, run client.py (one per player) by terminal.
<h3>Server</h3>
<p>To run the server, you must specify a port as an argument using <i>-o</i> or <i>--port</i>. For example:</p> 
<p align="center">>> python3 server.py --port 8000</p>
<p>Default port is 8080</p>

<h3>Client</h3>
<p>To run the client (one per player), you must specify the following arguments:</p>
<table>
  <tr>
    <th>Players</th>
    <th>Stages</th>
    <th>Name</th>
    <th>IP Address</th>
    <th>Port</th>
  </tr>
  <tr>
    <td><i>-p</i> or <i>--players</i></td>
    <td><i>-s</i> or <i>--stages</i></td>
    <td><i>-n</i> or <i>--name</i></td>
    <td><i>-i</i> or <i>--ip</i></td>
    <td><i>-o</i> or <i>--port</i></td>
  </tr>
</table>
<p>For example:</p>
<p align="center">>> python3 client.py -p 4 --stages 3 -n admurillo --ip 127.0.1.1 -o 8000</p>
<p>Default values for these arguments are (nickname is required):</p>
<b>Players: </b>1
<b>Stages: </b>1
<b>IP Address: </b>127.0.0.1
<b>Port: </b>8080
<p>IP Address and port must be the same as the server values</p>

<h3>Characters</h3>
<p>When you start a new game or you join a started game, you will choose a character: Bookworm, Worker, Procrastinator or Whatsapper.</p>
<p>Each one has its stats and its special skill specified before choosing one of them. When it's your turn, you can attack one random enemy or use your special skill.</p>
<h3>Enemies</h3>
<p>There are four enemies during the game: Partial Exam, Final Exam, Theoretical class and Teacher. Each one has its stats.
