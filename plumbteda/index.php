<!--Code started by Michael Ortega for the LIG-->
<!--October 10th, 2016-->

<!doctype html>
    <head> 
    <meta charset="UTF-8" />
    
    <script src="js/jquery-2.2.4.min.js"></script>
    <script src="bootstrap-3.3.7/js/bootstrap.min.js"></script>
    <script src="js/jsPlumb-2.1.7.js"></script>
    <link href="css/main.css" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="bootstrap-3.3.7/css/bootstrap.min.css">
    
    </head>
    
    <body>
        <div class="container theme-showcase" role="main">
            <table width="100%">
                <tr>
                    <td>
                        <h1><span class="label label-primary">Sakura</span></h1>
                        <p> Date Storage and Analysis</p>
                    </td>
                    <td align="right">
                        <div class="btn-group btn-group-xs">
                            <a class="btn btn-default btn-xs dropdown-toggle" type="button" id="dp_menu_user" data-toggle="dropdown"> Unknown user <span class="caret"></span></a>
                            <ul class="dropdown-menu" role="menu">
                                <li><a href="#" onclick="log_in()">Log in</a></li>
                                <li><a href="#" onclick="new_user()">New User</a></li>
                                <li><a href="#" onclick="log_out()">Log out</a></li>
                            </ul>
                        </div>
                    </td>
                </tr>
            </table>
            <div id ="sakura_menu_div" class="sakura_menu">
                <table width="100%">
                    <tr><td>
                        <div class="btn-group btn-group-xs">
                            <a class="btn btn-default btn-xs dropdown-toggle" type="button" id="dp_menu_project" data-toggle="dropdown"> Project <span class="fa fa-caret-down"></span></a>
                            <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                                <li><a href="#" onclick="new_project()">New</a></li>
                                <li><a href="#" onclick="load_project()">Load</a></li>
                                <li><a href="#" onclick="save_project()">Save</a></li>
                            </ul>
                        </div>
                        <div class="btn-group btn-group-xs">
                            <a class="btn btn-default btn-xs dropdown-toggle" type="button" id="dp_menu_Data" data-toggle="dropdown"> Dataset <span class="fa fa-caret-down"></span></a>
                            <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                                <li><a href="#" onclick="not_yet()">New</a></li>
                                <li><a href="#" onclick="select_data()">Select</a></li>
                                <li><a href="#" onclick="not_yet()">Import</a></li>
                            </ul>
                        </div>
                    </td>
                    <td align="right">
                        <div><button class="btn btn-default btn-xs" type="button" id="dp_menu_help" onclick="not_yet()">help</button></div>
                    </td>
                </table>
            </div>
            
            <table width="100%">
                <tr>
                    <td width="160px">
                        <div id="sakura_left_div" class="sakura_left_tab">
                        </div>
                    <td>
                        <div id="sakura_main_div" class="sakura_main">
                        </div>
            </table>
        </div>
        
        <div id="sakura_operator_contextMenu" class="dropdown clearfix">
            <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu" style="display:block;position:static;margin-bottom:5px;">
                <li><a tabindex="-1" href="#">Delete</a></li>
            </ul>
        </div>
        
        <footer class="footer">
            <hr width="100px">
            <p class="text-muted" align="center">Developed by and for the Laboratoire d'Informatique de Grenoble <br>(Universite Grenoble Alpes, CNRS, LIG)<br>
            Last update 15/11/2016</p>
        </footer>
        
        <script src="js/general.js"></script>
        <script src="js/main.js"></script>
        <script src="js/menus/connexion.js"></script>
        <script src="js/menus/menu_dataset.js"></script>
    
    </body>
</html>
