<?php

class UrlFormatter {
    public static function baseUrl() {
        $protocol = isset($_SERVER['HTTPS']) || ( ! empty($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] == 'https') ? 'https' : 'http';
        $server = $_SERVER['HTTP_HOST'];
        //$port = $_SERVER['SERVER_PORT'] != 80 ? ":{$_SERVER['SERVER_PORT']}" : '';
        $path = rtrim(Zend_Controller_Front::getInstance()->getBaseUrl(), '/\\') . '/';
        return "$protocol://$server$path";
    }

    public static function showLogoUrl() {
        return self::baseUrl()  . "api/show-logo?id=";
    }
}