<?php
/**
 * Created by PhpStorm.
 * User: Eddie
 * Date: 23/02/2017
 * Time: 20:18
 */

function createTree($dir){
    $html ='<div id="tree" class="tree"><ul>';
    $html .= exploreDir($dir,"");
    $html .= "</ul></div>";
    echo $html;
}
function exploreDir($dir,$str){
    if (is_dir($dir)) {
        if ($dh = opendir($dir)) {
            if(strrpos($dir, "/") > -1){
                $dirname = substr($dir,strrpos($dir, "/")+1);
            }
            else $dirname = $dir;
            $str .= "<li data-type=\"dir\" data-path='".$dir."' data-jstree='{ \"opened\" : true }'>".$dirname."<ul>";
            while (($file = readdir($dh)) !== false) {
                if($file != '.' && $file != '..')
                    //$str .= "fichier : $file : type : " . filetype($dir."/".$file) . "<br/>";
                    if(filetype($dir."/".$file) == "file"){
                        //$str .= "<li data-jstree='{\"icon\":\"//jstree.com/tree.png\"}'>".$file."</li>";
                        $str .= "<li data-type=\"file\" data-path='".$dir."/".$file."' class=\"file\" data-jstree='{\"icon\":\"http://www.planetminecraft.com/images/buttons/icon_edit.png\"}'>".$file."</li>";
                    }
                    elseif(filetype($dir."/".$file)){
                        $str = exploreDir($dir."/".$file,$str);
                    }
            }
            $str .= "</ul></li>";
            closedir($dh);
        }
    }
    return $str;
}

$path = "../".$_GET['path'];
createTree($path);
