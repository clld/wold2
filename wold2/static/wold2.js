WOLD = {}

CLLD.Map.style_maps["wold_meaning"] = new OpenLayers.StyleMap({
        "temporary": {
            label : "${name}: ${values}",
            pointRadius: 8,
            strokeColor: "black",
            strokeWidth: 1,
            fillColor: "orange",
            fillOpacity: 0.6,
            fontColor: "black",
            fontSize: "14px",
            fontFamily: "Arial",
            fontWeight: "bold",
            labelAlign: "cb",
            labelOutlineColor: "white",
            labelOutlineWidth: 4
        }
    });

CLLD.Map.style_maps["wold_languages"] = (function () {
    var styles = new OpenLayers.StyleMap({
        "default": {
            pointRadius: 8,
            strokeColor: "black",
            strokeWidth: 1,
            fillOpacity: 0.6,
            fillColor: 'red',
            graphicName: "circle",
            graphicXOffset: 50,
            graphicYOffset: 50,
            graphicZIndex: 20
        },
        "temporary": {
            pointRadius: 12,
            fillOpacity: 1,
            label : "${name}",
            fontColor: "black",
            fontSize: "12px",
            fontFamily: "Courier New, monospace",
            fontWeight: "bold",
            labelAlign: "cm",
            labelOutlineColor: "white",
            labelOutlineWidth: 3
        },
        "select": {
            label: "",
            pointRadius: 10
        }
    }),
        color = {'y': {fillColor: "red"}, 'n': {fillColor: "blue"}};
    styles.addUniqueValueRules("default", "recipient", color);
    return styles;
})();
