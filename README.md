# MEGANOUGHTSANDCROSSES

A Noughts and Crosses game of Noughts and Crosses boards! Your move determines which sub-grid your opponent must play in. For example, playing in the top-left of a grid would require your opponent to play in the top-left grid. If the grid has already been won, then the opponent can play anywhere.

This implementation works locally, over LAN and should work over the internet with correct port-forwarding (default port 37575), although I haven't verified that. It will also work using the server script as a proxy, but only in text mode (which can be forced by setting Text = True at the top of the main script).