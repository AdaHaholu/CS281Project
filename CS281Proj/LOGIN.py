import PySimpleGUI as sg
from datetime import datetime as date
import sqlite3 as sql
import socket

con = sql.connect("/VideoSharing.db")
crs = con.cursor()
vidattr = []
userattr = []
tagattr = []
typeattr = []

global videos
videos = []
for vAttr in crs.execute(
    """SELECT Name, DateOfUpload, view_count, Duration, email, like_count, dislike_count, description FROM Video ORDER BY videoID ASC"""
):
    vidattr.append(vAttr)
for vRow in vidattr:
    videos.append(
        [vRow[0], vRow[1], vRow[2], vRow[3], vRow[4], vRow[5], vRow[6], vRow[7]]
    )
for i in range(len(videos)):
    for tAttr in crs.execute(
        """SELECT tag_desc FROM Tag t, Video v WHERE v.tagID = t.tagID AND v.name = ?""",
        (videos[i][0],),
    ):
        videos[i].append(tAttr[0])
    for vtAttr in crs.execute(
        """SELECT v_type_desc FROM v_type vt, Video v WHERE vt.v_typeID = v.v_typeID AND v.name = ?""",
        (videos[i][0],),
    ):
        videos[i].append(vtAttr[0])
    for uAttr in crs.execute(
        """SELECT u.name FROM User u, Video v WHERE v.email = u.email AND v.name = ?""",
        (videos[i][0],),
    ):
        videos[i].append(uAttr[0])
    for vis in crs.execute(
        """SELECT Visibility FROM Video WHERE name = ?""", (videos[i][0],)
    ):
        videos[i].append(vis[0])
    for ID in crs.execute(
        """SELECT videoID FROM Video WHERE name = ?""", (videos[i][0],)
    ):
        videos[i].append(ID[0])


#######################################################################################
def login():
    layout = [
        [sg.Text("Choose login option: ")],
        [sg.Button("Standart"), sg.Button("Partner"), sg.Button("Admin")],
        [sg.Button("Quit")],
    ]
    window = sg.Window("Login Page", layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Quit":
            window.close()
            break
        elif event == "Standart":
            window.close()
            standart_login()
        elif event == "Partner":
            window.close()
            partner_login()
        elif event == "Admin":
            window.close()
            admin_login()


#######################################################################################
def standart_page(email):
    name = []
    for user in crs.execute("""SELECT name FROM User WHERE email = ?""", (email,)):
        name.append(user)
    layout = [
        [sg.Text("Welcome " + name[0][0])],
        [sg.Button("Search"), sg.Button("Logout")],
    ]

    window = sg.Window("Standart Page", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Logout":
            window.close()
            login()
        elif event == "Search":
            window.close()
            search(email)


#######################################################################################
def partner_page(email):
    name = []
    for user in crs.execute("""SELECT name FROM User WHERE email = ?""", (email,)):
        name.append(user)
    layout = [
        [sg.Text("Welcome " + name[0][0])],
        [sg.Button("My Videos"), sg.Button("My Payments"), sg.Button("Logout")],
    ]
    window = sg.Window("Partner Page", layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Logout":
            window.close()
            login()
        elif event == "My Videos":
            window.close()
            my_vid(email)
        elif event == "My Payments":
            window.close()
            my_payments(email)


#######################################################################################
def admin_page(email):
    name = []

    for user in crs.execute("""SELECT name FROM User WHERE email = ?""", (email,)):
        name.append(user)
    layout = [
        [sg.Text("Welcome " + name[0][0])],
        [
            sg.Button("All Videos", key="all"),
            sg.Button("All Payments", key="pay"),
            sg.Button("Assign Advertisement", key="ad"),
            sg.Button("Logout"),
        ],
    ]
    window = sg.Window("Admin Page", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Logout":
            window.close()
            login()
        elif event == "all":
            window.close()
            all_videos(email)
        elif event == "pay":
            window.close()
            payment(email)
        elif event == "ad":
            window.close()
            alter_ad(email)


#######################################################################################
def standart_login():
    email = []
    emailList = []
    pw = []
    pwList = []
    infoTable = []
    info = []
    for table in crs.execute("""SELECT email FROM User ORDER BY email"""):
        email.append(table)
    for mail in email:
        emailList.append(mail[0])
    for ptable in crs.execute("""SELECT password FROM User ORDER BY email"""):
        pw.append(ptable)
    for password in pw:
        pwList.append(password[0])
    for table in crs.execute("""SELECT email, password FROM User"""):
        infoTable.append(table)
    for row in infoTable:
        info.append((row[0], row[1]))

    layout = [
        [sg.Text("Email:")],
        [sg.Input(key="email")],
        [sg.Text("Password:")],
        [sg.Input(key="password", password_char="*")],
        [[sg.Text(key="out")]],
        [sg.Button("Back"), sg.Button("Login")],
    ]
    window = sg.Window("Standart User", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            login()
        elif event == "Login":
            if values["email"] in emailList:
                if values["password"] in pwList:
                    if (values["email"], values["password"]) in info:
                        window.close()
                        standart_page(values["email"])
                    else:
                        window["out"].update("Wrong password, please try again")
                elif values["password"] not in pwList:
                    window["out"].update("Wrong password, please try again")
            elif values["email"] not in emailList:
                window["out"].update("User not found")


#######################################################################################
def partner_login():
    p_infoTable = []
    p_info = []
    plist = []
    ppwlist = []
    p_all = []
    for table in crs.execute(
        """SELECT p.P_email, u.password FROM Partner p, User u WHERE p.P_email = u.email"""
    ):
        p_all.append(table)
    for mail in p_all:
        plist.append(mail[0])
        ppwlist.append(mail[1])
    for table in crs.execute(
        """SELECT p.P_email, u.password FROM User u, Partner p WHERE p.P_email = u.email """
    ):
        p_infoTable.append(table)
    for row in p_infoTable:
        p_info.append((row[0], row[1]))

    layout = [
        [sg.Text("Email:")],
        [sg.Input(key="email")],
        [sg.Text("Password:")],
        [sg.Input(key="password", password_char="*")],
        [[sg.Text(key="out")]],
        [sg.Button("Back"), sg.Button("Login")],
    ]
    window = sg.Window("Partner User", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            login()
        elif event == "Login":
            if values["email"] in plist:
                if values["password"] in ppwlist:
                    if (values["email"], values["password"]) in p_info:
                        window.close()
                        partner_page(values["email"])
                    else:
                        window["out"].update("Wrong password, please try again")
                elif values["password"] not in ppwlist:
                    window["out"].update("Wrong password, please try again")
            elif values["email"] not in plist:
                window["out"].update("User not found")


#######################################################################################
def admin_login():
    a_infoTable = []
    a_info = []
    alist = []
    apwlist = []
    a_all = []
    for table in crs.execute(
        """SELECT a.A_email, u.password FROM Admin a, User u WHERE a.A_email = u.email"""
    ):
        a_all.append(table)
    for mail in a_all:
        alist.append(mail[0])
        apwlist.append(mail[1])
    for table in crs.execute(
        """SELECT a.A_email, u.password FROM User u, Admin a WHERE a.A_email = u.email """
    ):
        a_infoTable.append(table)
    for row in a_infoTable:
        a_info.append((row[0], row[1]))

    layout = [
        [sg.Text("Email:")],
        [sg.Input(key="email")],
        [sg.Text("Password:")],
        [sg.Input(key="password", password_char="*")],
        [[sg.Text(key="out")]],
        [sg.Button("Back"), sg.Button("Login")],
    ]
    window = sg.Window("Admin User", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            login()
        elif event == "Login":
            if values["email"] in alist:
                if values["password"] in apwlist:
                    if (values["email"], values["password"]) in a_info:
                        window.close()
                        admin_page(values["email"])
                    else:
                        window["out"].update("Wrong password, please try again")
                elif values["password"] not in apwlist:
                    window["out"].update("Wrong password, please try again")
            elif values["email"] not in alist:
                window["out"].update("User not found")


#######################################################################################
def create_v_layout(videoName, Tag, UploadDate, v_type, view_count, duration, uploader):
    tDate = date.today().strftime("%d/%m/%Y")
    dateDiff = (int(tDate[:2]) + int(tDate[3:5]) * 30 + int(tDate[6:10]) * 365) - (
        int(UploadDate[:2]) + int(UploadDate[3:5]) * 30 + int(UploadDate[6:10]) * 365
    )
    layout = [
        ["Uploaded by: " + uploader],
        [
            "Uploaded "
            + str(
                dateDiff
                - ((dateDiff - (dateDiff // 365) * 365) // 30) * 30
                - (dateDiff // 365) * 365
            )
            + " Days "
            + str((dateDiff - (dateDiff // 365) * 365) // 30)
            + " Months "
            + str(dateDiff // 365)
            + " Years ago"
        ],
        ["Duration: " + str(duration)],
        [str(view_count) + " views"],
        ["Tag: " + str(Tag)],
        ["Type: " + str(v_type)],
    ]
    return layout


#######################################################################################
def search(email):
    dummyvid1 = []
    dummyvid2 = []
    dummyvid3 = []
    attributes = []
    lb1 = []
    layout = [
        [sg.Text("Enter keyword:"), sg.Input(key="keyword")],
        [
            sg.Button("Filter by tag", key="tag"),
            sg.Button("Filter by type", key="vtype"),
            sg.Button("Filter by name", key="vname"),
        ],
        [sg.Text(key="out")],
    ]
    videoID = []
    tagTable = []
    alltags = []
    typeTable = []
    alltypes = []
    nameTable = []
    allnames = []
    for el in crs.execute("""SELECT tag_desc FROM Tag"""):
        tagTable.append(el)
    for element in tagTable:
        alltags.append(element[0])
    for v_type in crs.execute("""SELECT v_type_desc FROM v_type"""):
        typeTable.append(v_type)
    for v_type2 in typeTable:
        alltypes.append(v_type2[0])
    for v_name in crs.execute("""SELECT name FROM Video"""):
        nameTable.append(v_name)
    for v_name2 in nameTable:
        allnames.append(v_name2[0])
    for table in crs.execute("""SELECT videoID FROM Video"""):
        videoID.append(table)
    for row in videoID:
        for name in crs.execute(
            """SELECT v.Name FROM Video v WHERE videoID = ?""", (row[0],)
        ):
            vname = name[0]
        lb1.append(vname)
    for vid in videos:
        if vid[11] == "False":
            lb1.remove(vid[0])
    layout.append(
        [
            sg.Listbox(lb1, size=(20, 10), enable_events=True, key="vids"),
            sg.Listbox(attributes, size=(40, 10), key="update"),
        ]
    )
    layout.append(
        [
            sg.Button("Go to video page", key="vpage"),
            sg.Button("Video Statistics", key="stat"),
            sg.Button("Back"),
        ]
    )
    window = sg.Window("Search", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            standart_page(email)
        elif event == "tag":
            for vid in videos:
                if vid[8] == values["keyword"] and vid[11] == "True":
                    dummyvid1.append(vid[0])
            if dummyvid1 == []:
                window["out"].update("No videos with tag: " + values["keyword"])
            else:
                window.close()
                search_tag(values["keyword"], email)

        elif event == "vtype":
            for vid in videos:
                if vid[9] == values["keyword"] and vid[11] == "True":
                    dummyvid2.append(vid[0])
            if dummyvid2 == []:
                window["out"].update("No videos with type: " + values["keyword"])
            else:
                window.close()
                search_vtype(values["keyword"], email)
        elif event == "vname":
            for vid in videos:
                if vid[0] == values["keyword"] and vid[11] == "True":
                    dummyvid3.append(vid[0])
            if dummyvid3 == []:
                window["out"].update("No videos with name: " + values["keyword"])
            else:
                window.close()
                search_name(values["keyword"], email)
        elif event == "stat":
            for vid in videos:
                for val in range(len(values["vids"])):
                    if vid[0] == values["vids"][val]:
                        attributes = create_v_layout(
                            vid[0], vid[8], vid[1], vid[9], vid[2], vid[3], vid[10]
                        )
                        window["update"].update(attributes)
                        attributes = []
        elif event == "vpage":
            for vids in videos:
                for vals in values["vids"]:
                    if vids[0] == vals:
                        vids[2] += 1
                        crs.execute(
                            """UPDATE Video SET view_count = ? WHERE Video.name = ?""",
                            (vids[2], values["vids"][0]),
                        )
                        con.commit()
                        window.close()
                        video_page(
                            vids[0],
                            vids[1],
                            vids[2],
                            vids[3],
                            vids[4],
                            vids[5],
                            vids[6],
                            vids[7],
                            vids[8],
                            vids[9],
                            vids[10],
                            email,
                        )


#######################################################################################
def search_tag(tag, email):
    attributes = []
    lb1 = []
    layout = []
    videoID = []
    tagTable = []
    alltags = []
    typeTable = []
    alltypes = []
    nameTable = []
    allnames = []
    for el in crs.execute("""SELECT tag_desc FROM Tag"""):
        tagTable.append(el)
    for element in tagTable:
        alltags.append(element[0])
    for v_type in crs.execute("""SELECT v_type_desc FROM v_type"""):
        typeTable.append(v_type)
    for v_type2 in typeTable:
        alltypes.append(v_type2[0])
    for v_name in crs.execute("""SELECT name FROM Video"""):
        nameTable.append(v_name)
    for v_name2 in nameTable:
        allnames.append(v_name2[0])
    for table in crs.execute(
        """SELECT videoID FROM Video WHERE Visibility = ?""", ("True",)
    ):
        videoID.append(table)
    for row in videoID:
        for name in crs.execute(
            """SELECT v.Name FROM Video v WHERE videoID = ?""", (row[0],)
        ):
            vname = name[0]
            lb1.append(vname)
    for vid in videos:
        if vid[8] != tag and vid[0] in lb1:
            lb1.remove(vid[0])  # hatalı
    layout.append(
        [
            sg.Listbox(lb1, size=(20, 10), enable_events=True, key="vids"),
            sg.Listbox(attributes, size=(40, 10), key="update"),
        ]
    )
    layout.append(
        [
            sg.Button("Go to video page", key="vpage"),
            sg.Button("Video Statistics", key="stat"),
            sg.Button("Back"),
        ]
    )
    window = sg.Window("Search", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == "Back":
            window.close()
            search(email)
        elif event == "stat":
            for vid in videos:
                for val in range(len(values["vids"])):
                    if vid[0] == values["vids"][val]:
                        attributes = create_v_layout(
                            vid[0], vid[8], vid[1], vid[9], vid[2], vid[3], vid[10]
                        )
                        window["update"].update(attributes)
                        attributes = []
        elif event == "vpage":
            for vids in videos:
                for vals in values["vids"]:
                    if vids[0] == vals:
                        vids[2] += 1
                        crs.execute(
                            """UPDATE Video SET view_count = ? WHERE Video.name = ?""",
                            (vids[2], values["vids"][0]),
                        )
                        con.commit()
                        window.close()
                        video_page(
                            vids[0],
                            vids[1],
                            vids[2],
                            vids[3],
                            vids[4],
                            vids[5],
                            vids[6],
                            vids[7],
                            vids[8],
                            vids[9],
                            vids[10],
                            email,
                        )


#######################################################################################
def search_vtype(vtype, email):
    attributes = []
    lb1 = []
    layout = []
    videoID = []
    tagTable = []
    alltags = []
    typeTable = []
    alltypes = []
    nameTable = []
    allnames = []
    for el in crs.execute("""SELECT tag_desc FROM Tag"""):
        tagTable.append(el)
    for element in tagTable:
        alltags.append(element[0])
    for v_type in crs.execute("""SELECT v_type_desc FROM v_type"""):
        typeTable.append(v_type)
    for v_type2 in typeTable:
        alltypes.append(v_type2[0])
    for v_name in crs.execute("""SELECT name FROM Video"""):
        nameTable.append(v_name)
    for v_name2 in nameTable:
        allnames.append(v_name2[0])
    for table in crs.execute("""SELECT videoID FROM Video"""):
        videoID.append(table)
    for row in videoID:
        for name in crs.execute(
            """SELECT v.Name FROM Video v WHERE videoID = ?""", (row[0],)
        ):
            vname = name[0]
        lb1.append(vname)
    for vid in videos:
        if vid[9] != vtype and vid[0] in lb1:
            lb1.remove(vid[0])
    layout.append(
        [
            sg.Listbox(lb1, size=(20, 10), enable_events=True, key="vids"),
            sg.Listbox(attributes, size=(40, 10), key="update"),
        ]
    )
    layout.append(
        [
            sg.Button("Go to video page", key="vpage"),
            sg.Button("Video Statistics", key="stat"),
            sg.Button("Back"),
        ]
    )
    window = sg.Window("Search", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == "Back":
            window.close()
            search(email)
        elif event == "stat":
            for vid in videos:
                for val in range(len(values["vids"])):
                    if vid[0] == values["vids"][val]:
                        attributes = create_v_layout(
                            vid[0], vid[8], vid[1], vid[9], vid[2], vid[3], vid[10]
                        )
                        window["update"].update(attributes)
                        attributes = []
        elif event == "vpage":
            for vids in videos:
                for vals in values["vids"]:
                    if vids[0] == vals:
                        vids[2] += 1
                        crs.execute(
                            """UPDATE Video SET view_count = ? WHERE Video.name = ?""",
                            (vids[2], values["vids"][0]),
                        )
                        con.commit()
                        window.close()
                        video_page(
                            vids[0],
                            vids[1],
                            vids[2],
                            vids[3],
                            vids[4],
                            vids[5],
                            vids[6],
                            vids[7],
                            vids[8],
                            vids[9],
                            vids[10],
                            email,
                        )


#######################################################################################
def video_page(
    videoName,
    UploadDate,
    view_count,
    duration,
    email,
    lcount,
    dlcount,
    description,
    Tag,
    v_type,
    uploader,
    email1,
):
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    layout = [
        [sg.Button(videoName), sg.Text("Uploaded by: " + uploader)],
        [
            sg.Text(
                "Uploaded in "
                + str(
                    UploadDate[:2]
                    + " "
                    + months[int(UploadDate[3:5]) - 1]
                    + " "
                    + UploadDate[6:10]
                )
            )
        ],
        [sg.Text("Duration: " + str(duration)), sg.Text(str(view_count) + " views")],
        [sg.Text("Tag: " + str(Tag))],
        [sg.Text("Type: " + str(v_type))],
        [
            sg.Button("Like"),
            sg.Text(str(lcount) + " likes", key="likecount"),
            sg.Button("Dislike"),
            sg.Text(str(dlcount) + " dislikes", key="dislikecount"),
        ],
        [sg.Button("Back")],
    ]
    window = sg.Window(videoName, layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            search(email1)
        elif event == "Like":
            crs.execute(
                """UPDATE Video SET like_count = ? WHERE Video.Name = ?""",
                (lcount + 1, videoName),
            )
            con.commit()
            for lk in videos:
                if lk[0] == videoName:
                    lk[5] = lcount + 1
            window["likecount"].update(str(lcount + 1) + " likes")
            window["dislikecount"].update(str(dlcount) + " dislikes")
        elif event == "Dislike":
            crs.execute(
                """UPDATE Video SET dislike_count = ? WHERE Video.Name = ?""",
                (dlcount + 1, videoName),
            )
            con.commit()
            for dlk in videos:
                if dlk[0] == videoName:
                    dlk[6] = dlcount + 1
            window["dislikecount"].update(str(dlcount + 1) + " dislikes")
            window["likecount"].update(str(lcount) + " likes")


#######################################################################################
def search_name(videoName, email):
    attributes = []
    lb1 = []
    layout = []
    videoID = []
    tagTable = []
    alltags = []
    typeTable = []
    alltypes = []
    nameTable = []
    allnames = []
    for el in crs.execute("""SELECT tag_desc FROM Tag"""):
        tagTable.append(el)
    for element in tagTable:
        alltags.append(element[0])
    for v_type in crs.execute("""SELECT v_type_desc FROM v_type"""):
        typeTable.append(v_type)
    for v_type2 in typeTable:
        alltypes.append(v_type2[0])
    for v_name in crs.execute("""SELECT name FROM Video"""):
        nameTable.append(v_name)
    for v_name2 in nameTable:
        allnames.append(v_name2[0])
    for table in crs.execute("""SELECT videoID FROM Video"""):
        videoID.append(table)
    for row in videoID:
        for name in crs.execute(
            """SELECT v.Name FROM Video v WHERE videoID = ?""", (row[0],)
        ):
            vname = name[0]
        lb1.append(vname)
    for vid in videos:
        if vid[0] != videoName and vid[0] in lb1:
            lb1.remove(vid[0])
    layout.append(
        [
            sg.Listbox(lb1, size=(20, 10), enable_events=True, key="vids"),
            sg.Listbox(attributes, size=(40, 10), key="update"),
        ]
    )
    layout.append(
        [
            sg.Button("Go to video page", key="vpage"),
            sg.Button("Video Statistics", key="stat"),
            sg.Button("Back"),
        ]
    )
    window = sg.Window("Search", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == "Back":
            window.close()
            search(email)
        elif event == "stat":
            for vid in videos:
                for val in range(len(values["vids"])):
                    if vid[0] == values["vids"][val]:
                        attributes = create_v_layout(
                            vid[0], vid[8], vid[1], vid[9], vid[2], vid[3], vid[10]
                        )
                        window["update"].update(attributes)
                        attributes = []
        elif event == "vpage":
            for vids in videos:
                for vals in values["vids"]:
                    if vids[0] == vals:
                        vids[2] += 1
                        crs.execute(
                            """UPDATE Video SET view_count = ? WHERE Video.name = ?""",
                            (vids[2], values["vids"][0]),
                        )
                        con.commit()
                        window.close()
                        video_page(
                            vids[0],
                            vids[1],
                            vids[2],
                            vids[3],
                            vids[4],
                            vids[5],
                            vids[6],
                            vids[7],
                            vids[8],
                            vids[9],
                            vids[10],
                            email,
                        )


#######################################################################################
def my_vid(email):
    vidlist = []
    atrlist = []
    partner1 = []
    partner2 = []
    for elt in crs.execute("""SELECT name FROM User WHERE email = ?""", (email,)):
        partner1.append(elt)
    for elt2 in partner1:
        partner2.append(elt2[0])
    for vid1 in videos:
        if vid1[10] == partner2[0]:
            vidlist.append(vid1[0])
    layout = [
        [
            sg.Listbox(vidlist, enable_events=True, size=(30, 10), key="myvids"),
            sg.Listbox(atrlist, enable_events=True, size=(30, 10), key="attr"),
        ],
        [sg.Text(key="out")],
        [
            sg.Button("Edit Video", key="edit"),
            sg.Button("See Stats", key="stats"),
            sg.Button("Create Video", key="new"),
            sg.Button("Delete Video", key="del"),
            sg.Button("Back"),
        ],
    ]

    window = sg.Window("My Videos", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            partner_page(email)
        elif event == "edit":
            for vid1 in videos:
                for val1 in range(len(values["myvids"])):
                    if vid1[0] == values["myvids"][val1]:
                        window.close()
                        edit_video(vid1[0], email)
        elif event == "stats":
            for vid in videos:
                for val in range(len(values["myvids"])):
                    if vid[0] == values["myvids"][val]:
                        atrlist = [
                            str(vid[5]) + " likes",
                            str(vid[6]) + " dislikes",
                            str(vid[2]) + " views",
                        ]
                        if vid[11] == "True":
                            atrlist.append("Visible")
                        elif vid[11] == "False":
                            atrlist.append("Not Visible")
                        window["attr"].update(atrlist)
                        atrlist = []
        elif event == "new":
            window.close()
            new_video(email)
        elif event == "del":
            dumvid = videos[:]
            for vidx in dumvid:
                for val in range(len(values["myvids"])):
                    if vidx[0] == values["myvids"][val]:
                        crs.execute(
                            """DELETE FROM Video WHERE videoID = ?""", (vidx[12],)
                        )
                        con.commit()
                        videos.remove(vidx)
                        vidlist.remove(vidx[0])
                        window["myvids"].update(vidlist)
                        window["out"].update("Video deleted")


#######################################################################################
def edit_video(vidname, email):
    layout = []
    tagTable = []
    alltags = []
    for el in crs.execute("""SELECT tag_desc FROM Tag ORDER BY tagID ASC"""):
        tagTable.append(el)
    for element in tagTable:
        alltags.append(element[0])
    for vid in videos:
        if vid[0] == vidname:
            layout = [
                [
                    sg.Text("Name: " + vidname + ","),
                    sg.Text("Enter new name: "),
                    sg.Input(key="newname", size=(10, 10)),
                    sg.Button("Change Name", key="name"),
                ],
                [
                    sg.Text("Description: " + vid[7] + ","),
                    sg.Text("Enter new description: "),
                    sg.Input(key="newdesc", size=(10, 10)),
                    sg.Button("Change Description", key="desc"),
                ],
                [
                    sg.Text("Tag: " + vid[8] + ","),
                    sg.Text("Enter new tag: "),
                    sg.Input(key="newtag", size=(10, 10)),
                    sg.Button("Change Tag", key="tag"),
                ],
                [sg.Text(key="out")],
                [sg.Button("Back")],
            ]
    window = sg.Window("Edit Video", layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            my_vid(email)
        elif event == "name":
            for vid1 in videos:
                if vid1[0] == vidname:
                    vid1[0] = values["newname"]
                    crs.execute(
                        """UPDATE Video SET name = ? WHERE videoID = ?""",
                        (values["newname"], vid1[12]),
                    )
                    con.commit()
                    window["out"].update("Name updated")
        elif event == "desc":
            for vid2 in videos:
                if vid2[0] == vidname:
                    vid2[7] = values["newdesc"]
                    crs.execute(
                        """UPDATE Video SET description = ? WHERE videoID = ?""",
                        (values["newdesc"], vid2[12]),
                    )
                    con.commit()
                    window["out"].update("Description updated")
        elif event == "tag":
            for vid3 in videos:
                if vid3[0] == vidname:
                    if values["newtag"] in alltags:
                        vid3[8] = values["newtag"]
                        crs.execute(
                            """UPDATE Video SET tagID = ? WHERE Video.videoID = ?""",
                            ((alltags.index(values["newtag"]) + 1) * 11, vid3[12]),
                        )
                        con.commit()
                    elif values["newtag"] not in alltags:
                        alltags.append(values["newtag"])
                        vid3[8] = values["newtag"]
                        crs.execute(
                            """INSERT INTO Tag (tagID, tag_desc) VALUES (?,?)""",
                            (len(alltags) * 11, values["newtag"]),
                        )
                        con.commit()
                        crs.execute(
                            """UPDATE Video SET tagID = ? WHERE videoID = ?""",
                            ((alltags.index(values["newtag"]) + 1) * 11, vid3[12]),
                        )
                        con.commit()
                    window["out"].update("Tag updated")


#######################################################################################
def new_video(email):
    tagTable = []
    alltags = []
    types = []
    alltypes = []
    ads = []
    allads = []
    for x in crs.execute("""SELECT Name FROM User WHERE email = ?""", (email,)):
        name = x[0]
    for el in crs.execute("""SELECT tag_desc FROM Tag ORDER BY tagID ASC"""):
        tagTable.append(el)
    for element in tagTable:
        alltags.append(element[0])
    for v_type in crs.execute(
        """SELECT v_type_desc FROM v_type ORDER BY v_typeID ASC"""
    ):
        types.append(v_type)
    for v_type2 in types:
        alltypes.append(v_type2[0])
    for ad1 in crs.execute("""SELECT a_type_desc FROM a_type ORDER BY a_typeID ASC"""):
        ads.append(ad1)
    for ad2 in ads:
        allads.append(ad2[0])
    layout = [
        [sg.Text("Enter name: "), sg.Input(key="name")],
        [sg.Text("Enter tag: "), sg.Input(key="tag")],
        [sg.Text("Enter duration: "), sg.Input(key="dur")],
        [sg.Text("Enter description: "), sg.Input(key="desc")],
        [sg.Text("Select type"), sg.Combo(alltypes, key="type")],
        [sg.Text("Select advertisement type"), sg.Combo(allads, key="ad")],
        [sg.Text(key="out")],
        [sg.Button("Create Video", key="new"), sg.Button("Back")],
    ]
    window = sg.Window("New Video", layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            my_vid(email)
        elif event == "new":
            if values["tag"] in alltags:
                if ":" in values["dur"]:
                    if values["dur"][: values["dur"].index(":")].isnumeric() == True:
                        if (
                            values["dur"][values["dur"].index(":") + 1 :].isnumeric()
                            == True
                        ):
                            if values["type"] != "":
                                if values["ad"] != "":
                                    videos.append(
                                        [
                                            values["name"],
                                            date.today().strftime("%d/%m/%Y"),
                                            0,
                                            values["dur"],
                                            email,
                                            0,
                                            0,
                                            values["desc"],
                                            values["tag"],
                                            values["type"],
                                            name,
                                            "False",
                                            len(videos),
                                        ]
                                    )
                                    crs.execute(
                                        """INSERT INTO Video (videoID, tagID, v_typeID, a_typeID,
                                                    email, DateOfUpload, IP_Adress,like_count, 
                                                    view_count, dislike_count, Description, Name,
                                                    Duration, Visibility) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                        (
                                            len(videos),
                                            (alltags.index(values["tag"]) + 1) * 11,
                                            alltypes.index(values["type"]) + 101,
                                            allads.index(values["ad"]) + 21,
                                            email,
                                            date.today().strftime("%d/%m/%Y"),
                                            socket.gethostbyname(socket.gethostname()),
                                            0,
                                            0,
                                            0,
                                            values["desc"],
                                            values["name"],
                                            values["dur"],
                                            "False",
                                        ),
                                    )
                                    con.commit()
                                    window["out"].update("Video created")
                                else:
                                    window["out"].update("Select advertisement type")
                            else:
                                window["out"].update("Select video type")
                        else:
                            window["out"].update("Enter valid duration (mm:ss)")
                    else:
                        window["out"].update("Enter valid duration (mm:ss)")
                else:
                    window["out"].update("Enter valid duration (mm:ss)")
            elif values["tag"] not in alltags:
                if ":" in values["dur"]:
                    if values["dur"][: values["dur"].index(":")].isnumeric() == True:
                        if (
                            values["dur"][values["dur"].index(":") + 1 :].isnumeric()
                            == True
                        ):
                            if values["type"] != "":
                                if values["ad"] != "":
                                    alltags.append(values["tag"])
                                    videos.append(
                                        [
                                            values["name"],
                                            date.today().strftime("%d/%m/%Y"),
                                            0,
                                            values["dur"],
                                            email,
                                            0,
                                            0,
                                            values["desc"],
                                            values["tag"],
                                            values["type"],
                                            name,
                                            "False",
                                            len(videos),
                                        ]
                                    )
                                    crs.execute(
                                        """INSERT INTO Tag(tagID, tag_desc) VALUES (?,?)""",
                                        (len(alltags) * 11, values["tag"]),
                                    )
                                    con.commit()
                                    crs.execute(
                                        """INSERT INTO Video (videoID, tagID, v_typeID, a_typeID,
                                                    email, DateOfUpload, IP_Adress,like_count, 
                                                    view_count, dislike_count, Description, Name,
                                                    Duration, Visibility) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                        (
                                            len(videos),
                                            (alltags.index(values["tag"]) + 1) * 11,
                                            alltypes.index(values["type"]) + 101,
                                            allads.index(values["ad"]) + 21,
                                            email,
                                            date.today().strftime("%d/%m/%Y"),
                                            socket.gethostbyname(socket.gethostname()),
                                            0,
                                            0,
                                            0,
                                            values["desc"],
                                            values["name"],
                                            values["dur"],
                                            "False",
                                        ),
                                    )
                                    con.commit()
                                    window["out"].update("Video created")
                                else:
                                    window["out"].update("Select advertisement type")
                            else:
                                window["out"].update("Select video type")
                        else:
                            window["out"].update("Enter valid duration (mm:ss)")
                    else:
                        window["out"].update("Enter valid duration (mm:ss)")
                else:
                    window["out"].update("Enter valid duration (mm:ss)")


#######################################################################################
def my_payments(email):
    p = []
    allp = []
    pn = []
    pi = []
    for p1 in crs.execute("""SELECT * FROM Payment WHERE P_email = ?""", (email,)):
        p.append(p1)
    for p2 in p:
        allp.append([p2[0], p2[1], p2[3]])
    for k in allp:
        pn.append(str(k[2]) + "$")
    layout = [
        [
            sg.Listbox(pn, size=(22, 10), key="pn"),
            sg.Listbox(pi, size=(22, 10), key="pi"),
        ],
        [sg.Text(key="out")],
        [sg.Button("Details", key="det"), sg.Button("Back")],
    ]
    window = sg.Window("My Payments", layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == "Back":
            window.close()
            partner_page(email)
        if event == "det":
            for x in allp:
                if str(x[2]) + "$" == values["pn"][0]:
                    pi = ["TNO: " + str(x[0]), "CompanyIBAN: " + str(x[1])]
                    window["pi"].update(pi)


#######################################################################################
def payment(email):
    empty = []
    part = []
    comp = []
    asc = []
    info = []
    name = []
    partner = []
    company = []
    associate = []
    pname = []
    vids = []
    cname = []
    ads = []
    display = []
    asx = []
    advertisement = []
    payment = []
    payment2 = []
    for p1 in crs.execute("""SELECT TransactionNo FROM Payment"""):
        payment2.append(p1)
    for p2 in payment2:
        payment.append(p2[0])
    for a in crs.execute("""SELECT * FROM Company"""):
        comp.append(a)
    for b in comp:
        company.append([b[0], b[1], b[2]])
    for c in crs.execute("""SELECT * FROM Partner"""):
        part.append(c)
    for k in crs.execute(
        """SELECT u.Name, u.email FROM User u, Partner p WHERE u.email = p.P_email"""
    ):
        name.append(k)
    for d in part:
        partner.append([d[0], d[1]])
    for z in name:
        for w in partner:
            if w[0] == z[1]:
                partner[partner.index(w)].append(z[0])
                pname.append(z[0])
    for x in company:
        for f in crs.execute(
            """SELECT ad_id, CompanyIBAN FROM has WHERE CompanyIBAN = ?""", (x[0],)
        ):
            asc.append(f)
    for x2 in range(len(company)):
        for e in asc:
            if e[1] == company[x2][0]:
                company[x2].append(e[0])
    for o in partner:
        for l in crs.execute(
            """SELECT ad_id, email FROM Video WHERE email = ?""", (o[0],)
        ):
            vids.append(l)
    for ş in vids:
        for ğ in partner:
            if ğ[0] == ş[1]:
                partner[partner.index(ğ)].append(ş[0])
    for i in partner:
        for j in company:
            if i[3] == j[3]:
                associate.append([i[2], i[0], j[2], j[0]])
    for y in company:
        cname.append(y[2])
    for u in company:
        for t in crs.execute(
            """SELECT name, ad_id FROM Advertisement WHERE ad_id = ?""", (u[3],)
        ):
            ads.append(t)
    for r in ads:
        for r1 in company:
            if r[1] == r1[3]:
                advertisement.append([r[0], r[1]])

    layout = [
        [
            sg.Button("List Partner", key="part"),
            sg.Button("List Company", key="comp"),
            sg.Button("List Advertisement", key="ad"),
            sg.Button("List Associate", key="asc"),
            sg.Button("List Payment", key="pinfo"),
        ],
        [
            sg.Listbox(empty, size=(30, 10), key="pc"),
            sg.Listbox(info, size=(30, 10), key="info"),
        ],
        [sg.Input(key="input"), sg.Button("Make Payment ($)", key="pay")],
        [sg.Text(key="out")],
        [sg.Button("Back")],
    ]
    window = sg.Window("Payment", layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            admin_page(email)
        elif event == "part":
            window["pc"].update(pname)
        elif event == "comp":
            window["pc"].update(cname)
        elif event == "ad":
            for cx in company:
                for val in range(len(values["pc"])):
                    if cx[2] == values["pc"][val]:
                        for x2 in advertisement:
                            if x2[1] == cx[3]:
                                display.append(x2[0])

            window["info"].update(display)
        elif event == "asc":
            for cx1 in company:
                for val in range(len(values["pc"])):
                    if cx1[2] == values["pc"][val]:
                        for asc in associate:
                            if cx1[2] == asc[2]:
                                asx.append(asc[0])
            window["info"].update(asx)
            asx = []
        elif event == "pay":
            if values["input"] != "":
                if values["input"].isnumeric() == True:
                    for ab in associate:
                        if [ab[2]] == values["pc"] and [ab[0]] == values["info"]:
                            crs.execute(
                                """INSERT INTO Payment (TransactionNo, CompanyIBAN, P_email, amount) VALUES (?,?,?,?)""",
                                (len(payment) + 1, ab[3], ab[1], values["input"]),
                            )
                            con.commit()
                            payment += [len(payment) + 1]
                            window["out"].update("Payment successful!")
                        else:
                            window["out"].update("Select company and partner")
                else:
                    window["out"].update("Input numeric amount to pay")
            else:
                window["out"].update("Input numeric amount to pay")
        elif event == "pinfo":
            for px in partner:
                if px[2] == values["pc"][0]:
                    l1 = []
                    l2 = []
                    for t1 in crs.execute(
                        """SELECT TransactionNo, amount FROM Payment WHERE P_email = ?""",
                        (px[0],),
                    ):
                        l1.append(t1)
                    for t2 in l1:
                        l2.append(["TNO: " + str(t2[0]), "Amount: " + str(t2[1])])
                    window["info"].update(l2)


#######################################################################################
def all_videos(email):
    allvideos = []
    pending = []
    layout = [
        [
            sg.Button("Show Pending Videos", key="pending"),
            sg.Button("Show All Videos", key="all"),
        ]
    ]
    videoID = []
    nameTable = []
    allnames = []
    for v_name in crs.execute("""SELECT name FROM Video"""):
        nameTable.append(v_name)
    for v_name2 in nameTable:
        allnames.append(v_name2[0])
    for table in crs.execute("""SELECT videoID FROM Video"""):
        videoID.append(table)
    for row in videoID:
        for name in crs.execute(
            """SELECT v.Name FROM Video v WHERE videoID = ?""", (row[0],)
        ):
            vname = name[0]
        allvideos.append(vname)
    for vid in videos:
        if vid[11] == "False":
            pending.append(vid[0])
    layout.append(
        [sg.Listbox(allvideos, size=(30, 10), enable_events=True, key="vids")]
    )
    layout.append([sg.Button("Alter Visibility", key="alter"), sg.Button("Back")])
    window = sg.Window("Search", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            admin_page(email)
        elif event == "pending":
            window["vids"].update(pending)
        elif event == "all":
            window["vids"].update(allvideos)
        elif event == "alter":
            for vidx in videos:
                for val in range(len(values["vids"])):
                    if vidx[0] == values["vids"][val]:
                        if vidx[11] == "True":
                            crs.execute(
                                """UPDATE Video SET Visibility = ? WHERE videoID = ?""",
                                ("False", vidx[12]),
                            )
                            con.commit()
                            videos[videos.index(vidx)][11] = "False"
                            allvideos.remove(vidx[0])
                        elif vidx[11] == "False":
                            crs.execute(
                                """UPDATE Video SET Visibility = ? WHERE videoID = ?""",
                                ("True", vidx[12]),
                            )
                            con.commit()
                            videos[videos.index(vidx)][11] = "True"
                            pending.remove(vidx[0])
                            window["vids"].update(pending)


#######################################################################################
def alter_ad(email):
    alladless = []
    allnames = []
    ads = []
    allads = []
    allattributes = []
    for el in crs.execute(
        """SELECT videoID, name, a_typeId FROM Video WHERE ad_id IS NULL"""
    ):
        alladless.append(el)
    for el1 in alladless:
        allattributes.append([el1[0], el1[1], el1[2]])
        allnames.append(el1[1])
    for el3 in crs.execute("""SELECT * FROM Advertisement"""):
        ads.append(el3)
    for el4 in range(len(allattributes)):
        for el5 in ads:
            if allattributes[el4][2] == el5[1]:
                allattributes[el4] += [el5[0], el5[1], el5[2], el5[3], el5[4]]

    layout = [
        [
            sg.Listbox(allnames, size=(30, 10), key="disp"),
            sg.Listbox(allads, size=(30, 10), key="ads"),
        ],
        [sg.Text(key="out")],
        [
            sg.Button("Show Preferences", key="show"),
            sg.Button("Details", key="detail"),
            sg.Button("Assign", key="assign"),
            sg.Button("Back"),
        ],
    ]
    window = sg.Window("Alter Ad", layout)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Back":
            window.close()
            admin_page(email)
        if event == "show":
            for vidx in allattributes:
                for val in range(len(values["disp"])):
                    if vidx[1] == values["disp"][val]:
                        allads = [vidx[5]]
                        window["ads"].update(allads)
        if event == "detail":
            for adx in allattributes:
                for val in range(len(values["ads"])):
                    if adx[5] == values["ads"][val]:
                        allads = [
                            "Name: " + str(adx[5]),
                            "Ad ID: " + str(adx[3]),
                            "Ad Type ID: " + str(adx[4]),
                            "Content: " + str(adx[6]),
                            "Flag: " + str(adx[7]),
                        ]
                        window["ads"].update(allads)
        if event == "assign":
            for x in allattributes:
                for valx in range(len(values["ads"])):
                    if x[5] == values["ads"][valx]:
                        crs.execute(
                            """UPDATE Video SET ad_id = ? WHERE videoID = ?""",
                            (x[3], x[0]),
                        )
                        con.commit()
                        allnames.remove(x[1])
                        window["disp"].update(allnames)
                        window["ads"].update([])
            window["out"].update("Assignment complete")


login()
