#!/usr/bin/php
<?php

function foo() {
    global $globalList;
    $globalList = 'ddd';
    $arg1 = 'a';
    this->bar($globalList, "b");
}
function bar( $myList ) {
    global $globalRunCount;
    $globalRunCount = $globalRunCount + 1;
    if ( $globalRunCount < 2 ) {
        bar($myList);
    }
    print "hello\n";
    baz();
}
function baz(string $catalogueUrl, $test) {
    global $globalList;

    print "world $globalList\n";

    return $globalList;
}

// $globalRunCount = 'select avg_rating, rating_count from ratings where sku = ?';
$globalList = array($globalRunCount, 'b');
$ttt = foo();
foo($globalList);
logger->bar();
$this->logger->test->error('failed to connect to catalogue', 'test');

