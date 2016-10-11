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
            <h1><span class="label label-primary">Plumbteda</span></h1>
            <p> Plumbery for Panteda Analysis</p>
            <div id ="ptda_menu_div" class="ptda_menu_tab">
                <div class="dropdown">
                    <button class="btn btn-default btn-xs dropdown-toggle" type="button" id="dp_menu_project" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
                        Project
                        <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                        <li><a href="#" onclick="new_project()">New</a></li>
                        <li><a href="#" onclick="load_project()">Load</a></li>
                        <li><a href="#" onclick="save_project()">Save</a></li>
                    </ul>
                </div>
            </div>
            
            <div id="ptda_main_div" class="ptda_main">
                <table border=0 cellspacing=0 cellpadding=0>
                <tr><td><div id="ptda_op_div" class="ptda_operators_tab"></div></td>
                    <td><div id="ptda_graph_div" class="ptda_graph_tab"></div></td>
                </table>
            </div>
        </div>
        
        <div id="ptda_operator_contextMenu" class="dropdown clearfix">
            <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu" style="display:block;position:static;margin-bottom:5px;">
                <li><a tabindex="-1" href="#">Delete</a></li>
            </ul>
        </div>
        
        <footer class="footer">
            <hr width="100px">
            <p class="text-muted" align="center">Developed by Etienne DUBLE and Michael ORTEGA (Univ. Grenoble Alpes, CNRS, LIG)<br>
            Last update 10/10/2016</p>
        </footer>
        
        <script src="js/main.js"></script>
    
    </body>
</html>
