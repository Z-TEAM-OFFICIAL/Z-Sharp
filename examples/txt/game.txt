~ ZEGA Turbo UI Example
win_title{ZEGA High-Performance Workstation}
win_w{800}
win_h{600}
fps{144}

~ Define an interactive button at X:200, Y:200 with Size:100x50
win_button{new *{200, 200}* *{100, 50}*}

print{ Launching GPU Window... }
print{ Turbo Target: 144 FPS }
boot{}