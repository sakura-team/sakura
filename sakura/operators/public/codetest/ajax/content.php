<?php

//echo $_GET['path'];
$file = file($_GET['path']);
$content = "";
foreach ($file as $line) {
    $content .=$line;
}
echo $content;

?>
