<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Http;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

function logRequest(Request $request, $response): void
{
    $startTime = defined('LARAVEL_START') ? LARAVEL_START : microtime(true);
    $processTime = (microtime(true) - $startTime) * 1000;

    echo sprintf(
        "DEBUG: %s %s - Status: %d - %.2fms\n",
        $request->method(),
        $request->path(),
        $response->getStatusCode(),
        $processTime
    );
}

Route::get('/', function () {
    $response = response()->json([
        'message' => 'Servidor WildInfo Arriba',
        'status' => 200
    ]);
    logRequest(request(), $response);
    return $response;
});

Route::get('/wildinfo/{name_or_id}', function (string $name_or_id): JsonResponse {
    $externalUrl = "https://api.api-ninjas.com/v1/animals?name=" . strtolower($name_or_id);
    $apiKey = env('API_NINJS_KEY', '');

    try {
        $response = Http::withHeaders([
            'X-Api-Key' => $apiKey,
        ])->get($externalUrl);

        echo "DEBUG EXTERNO: Ninjas API respondió con " . $response->status() . "\n";

        if ($response->status() === 404) {
            $jsonResponse = response()->json([
                'error' => 'animal no encontrado'
            ], 404);
            logRequest(request(), $jsonResponse);
            return $jsonResponse;
        }

        $data = $response->json();

        if (empty($data)) {
            $jsonResponse = response()->json([
                'error' => 'animal no encontrado'
            ], 404);
            logRequest(request(), $jsonResponse);
            return $jsonResponse;
        }

        $animalData = [
            'nombre' => $data[0]['name'],
            'reino' => $data[0]['taxonomy']['kingdom'],
            'clase' => $data[0]['taxonomy']['class'],
            'familia' => $data[0]['taxonomy']['family']
        ];

        $jsonResponse = response()->json($animalData);
        logRequest(request(), $jsonResponse);
        return $jsonResponse;

    } catch (\Exception $e) {
        $jsonResponse = response()->json([
            'error' => 'Servicio externo no disponible'
        ], 503);
        logRequest(request(), $jsonResponse);
        return $jsonResponse;
    }
});
