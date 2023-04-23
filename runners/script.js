require([
    "esri/WebMap",
    "esri/views/MapView",
    "esri/config"
], function (WebMap, MapView, esriConfig) {
    esriConfig.apiKey = "AAPK75685d3037644591b3df07a23b1d3ef7-SExUoNSF4x0zsDJO-hooTiLp2QPoF6-kOmznnuBESt0xTPwrqRkIXdZBUMmRSql";

    // Create a WebMap instance
    var webmap = new WebMap({
        portalItem: {
            id: "YOUR_WEBMAP_ID"
        }
    });

    // Create a MapView instance
    var view = new MapView({
        container: "viewDiv",
        map: webmap
    });
});