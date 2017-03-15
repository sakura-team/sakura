<?php
/**
 * Created by PhpStorm.
 * User: Eddie
 * Date: 10/02/2017
 * Time: 18:54
 */

$path = $_GET['path'];
$content = rawurldecode($_GET['content']);
//$path = substr($path,0,strrpos($path, "."))."_test".substr($path,strrpos($path, "."),strlen($path));
$path = substr($path,0,strrpos($path, ".")).substr($path,strrpos($path, "."),strlen($path));

unlink($path);

$file = fopen($path, 'a');
fputs($file, $content);
fclose($file);
