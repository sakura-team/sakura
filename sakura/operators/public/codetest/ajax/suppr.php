<?php
/**
 * Created by PhpStorm.
 * User: Eddie
 * Date: 05/03/2017
 * Time: 21:08
 */
$path = $_GET['path'];
echo $path;

echo "<br/>";
if(is_dir($path)){
    rmdir($path);
    echo "dir";
}
else{
    echo "file";
    unlink($path);
}

