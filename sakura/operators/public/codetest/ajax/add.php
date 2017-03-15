<?php
/**
 * Created by PhpStorm.
 * User: Eddie
 * Date: 23/02/2017
 * Time: 22:06
 */
$mode = $_GET['mode'];
$path = $_GET['path'];

if($mode === "dir"){
    if (!mkdir($path, 0777, true)) {
        die('Echec lors de la création des répertoires...');
    }
}
else if($mode === "file"){
    $file = fopen($path, 'a');
    fclose($file);
}
