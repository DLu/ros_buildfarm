<!DOCTYPE html>
<html>
<head>
  <title>@title - @start_time_local_str</title>
  <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>

  <script type="text/javascript" src="js/moment.min.js"></script>
  <script type="text/javascript" src="js/zepto.min.js"></script>
  </script>
  <script src="http://code.jquery.com/jquery-2.0.3.min.js"></script>
  <script src="http://culmat.github.io/jsTreeTable/treeTable.js"></script>
  <script type="text/javascript" src="js/setup.js"></script>

  <link rel="stylesheet" type="text/css" href="css/status_page.css" />
  <style>
  tbody tr td span { display: inline; }
  .organization { font-size: 130%; }
  .repo { font-size: 115%; }
  </style>
</head>
<body>
  <script type="text/javascript">
    window.body_ready_with_age(moment.duration(moment() - moment("@start_time", "X")));
  </script>
  <div class="top logo search">
    <h1><img src="http://wiki.ros.org/custom/images/ros_org.png" alt="ROS.org" width="150" height="32" /></h1>
    <h2>@title</h2>
  </div>
  <div class="top age">
    <p>This should show the age of the page...</p>
  </div>
  <table id="table">
    <caption></caption>
    <thead>
    <tr><th>Name
    @[for distro in distros]@
    <th><div>@distro</div>
    @[end for]@
    </thead>
    <tbody>
    @[for org in sorted(super_status, key=lambda d: d.lower())]@
    <tr data-tt-id="O@org" data-tt-level="1"><td class="organization">@org
        @[for distro in distros]@
        @[if distro in super_status[org]['status'] ]@
        <td>@super_status[org]['status'][distro]
        @[else]
        <td>
        @[end if]
        @[end for]@
    </tr>
        @[for repo in sorted(super_status[org]['repos'])]@
        <tr data-tt-id="R@repo" data-tt-parent-id="O@org" data-tt-level="2"><td class="repo">@repo
            @[for distro in distros]@
            @[if distro in super_status[org]['repos'][repo]['status'] ]@
            <td>@super_status[org]['repos'][repo]['status'][distro]
            @[else]
            <td>
            @[end if]
            @[end for]@
        </tr>
            @[for pkg in sorted(super_status[org]['repos'][repo]['pkgs'])]@
            <tr data-tt-id="@pkg" data-tt-parent-id="R@repo" data-tt-level="3"><td class="pkg">@pkg
                @[for distro in distros]@
                @[if distro in super_status[org]['repos'][repo]['pkgs'][pkg]['status'] ]@
                <td>@super_status[org]['repos'][repo]['pkgs'][pkg]['status'][distro]
                @[else]
                <td>
                @[end if]
                @[end for]@
            </tr>
            @[end for]@
        @[end for]@
    @[end for]@
    </tbody>

    <script type="text/javascript">
        com_github_culmat_jsTreeTable.register(this);
        treeTable($('#table'))
        window.tbody_ready();
    </script>
  </table>
  <script type="text/javascript">window.body_done();</script>
</body>
</html>
