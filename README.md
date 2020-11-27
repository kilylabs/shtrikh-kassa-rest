# shtrikh-kassa-rest
Простой HTTP REST сервер для фискального регистратора Штрих-М ФР (К)
    
Изначально разрабатывался для работы на Raspberry Pi, но может работать и на любом linux-сервере. 

Сделан на основе:
- [EVE](http://python-eve.org/)
- [Python-драйвер для Штрих-М ФР](https://github.com/rosix-ru/shtrihm-fr)

В качестве хранилица данных в REST-обмене используется MongoDB, но можно настроить и SQL (смотри документацию EVE)

Установка
------------

Для работы REST-сервера понадобится установка дополнительных модулей:
```bash
$ pip install eve pyserial
```

```bash
$ git clone https://github.com/kilylabs/shtrikh-kassa-rest.git
$ cd shtrikh-kassa-rest
$ git submodule init
$ git submodule update
$ cp kkm_conf.dist.py kkm_conf.py
$ vim kkm_conf.py # edit some settings
$ sudo python run.py
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

Использование
-----

Пример печати обычного чека (на PHP):

```php
<?php

// composer require "guzzlehttp/guzzle:5.*"

use GuzzleHttp\Client;

require 'vendor/autoload.php';

$guzzle = new Client([
    'base_url'=>'http://localhost:5000',
    'verify'=>false,
    'debug'=>true,
]);

try{

    $positions = [];

    $positions[] = [
        'art'=>'123',
        'name'=>'TAIMYR LIMIT EDITION',
        'price'=>(float)'100.10',
        'quantity'=>1,
        'discount'=>0
    ];
    $positions[] = [
        'art'=>'321',
        'name'=>'YAMAL',
        'price'=>(float)'200.20',
        'quantity'=>2,
        'discount'=>0
    ];

    $resp = $guzzle->post('/checks',[
        'json'=>[
            'client_name'=>'Василий',
            'order_id'=>'K-118232ssa',
            'type'=>'sale',
            'subtype'=>'card',
            'barcode'=>1,
            'positions'=>$positions,
        ],
    ]);
} catch(GuzzleHttp\Exception\ClientException $e) {
    var_dump($e->getResponse()->json());
    die();
}
```

Полное описание REST-интерфейса можно посмотреть [здесь](https://github.com/kilylabs/shtrikh-kassa-rest/blob/master/lib/rest_conf.py)
