<?php

echo "Hello from PHP-FPM";

$app = require __DIR__.'/../bootstrap/app.php';

$kernel = $app->make(Illuminate\Contracts\Http\Kernel::class);

$request = Illuminate\Http\Request::create('/', 'GET');

$response = $kernel->handle($request);

echo $response->getContent();
