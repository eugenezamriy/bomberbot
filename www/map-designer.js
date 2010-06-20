// -*- mode:espresso; coding:utf-8; -*-
/**
 * created: 19.06.2010 22:05
 * description: Bomberbot map designer.
 */

// BUG: regeneration of map with different size brokes image


Ext.ns("Bomber.MapEditor");


Bomber.MapEditor.DEFAULT_HEIGHT = 20;             // default map height (cells)
Bomber.MapEditor.DEFAULT_WIDTH = 20;              // default map width (cells)
Bomber.MapEditor.SPACE = 2;                       // space between cells (pixels)
Bomber.MapEditor.LENGTH = 20;                     // cell's side length
Bomber.MapEditor.FREE_BG_COLOR = "#99CC66";       // free cell color
Bomber.MapEditor.WALL_BG_COLOR = "brown";         // stone wall color
Bomber.MapEditor.STEEL_BG_COLOR = "gray";         // steel wall color
Bomber.MapEditor.BOT_BG_COLOR = "blue";           // player's cell color
// internal only variables
Bomber.MapEditor.PAPER = null;                    // paper element
Bomber.MapEditor.MAP = null;                      // map storage
Bomber.MapEditor.MAP_HEIGHT = undefined;          // current map height (cells)
Bomber.MapEditor.MAP_WIDTH = undefined;           // current mape width (cells)


/**
 * Submits created map to server.
 * TODO: must be completed later.
 */
Bomber.MapEditor.submitMap = function() {
    var bme = Ext.ns("Bomber.MapEditor");
    if (bme.MAP == null) {
        alert("Error: map must be generated");
        return;
    }
    var map_name = Ext.get("map-name-fld").dom.value.trim();
    if (map_name == "") {
        alert("Error: map name required");
        return;
    }
    var js = { map_name: map_name,
               map_height: bme.MAP_HEIGHT,
               map_width: bme.MAP_WIDTH,
               min_players_count: parseInt(Ext.get("min-players-fld").dom.value),
               max_players_count: parseInt(Ext.get("max-players-fld").dom.value),
               bonuses: { bomb: parseInt(Ext.get("bomb-fld").dom.value),
                          radius: parseInt(Ext.get("radius-fld").dom.value) },
               players: [],
               metal: [],
               stone: [] }
    var cell = null;
    for (var y = 0; y < bme.MAP_HEIGHT; y++) {
        for (var x = 0; x < bme.MAP_WIDTH; x++) {
            cell = bme.MAP[y][x];
            if (cell.attrs.fill == bme.WALL_BG_COLOR)
                js.stone.push([x, y]);
            else if (cell.attrs.fill == bme.STEEL_BG_COLOR)
                js.metal.push([x, y]);
            else if (cell.attrs.fill == bme.BOT_BG_COLOR)
                js.players.push([x, y]);
        }
    }
    alert(Ext.encode(js));
};


/**
 * Cell's click/double-click handler.
 */
Bomber.MapEditor.clickHandler = function(block, select, event) {
    var bme = Ext.ns("Bomber.MapEditor");
    var t = Ext.get(select).dom.value;
    if (t == "wall")
        block.attr({fill: bme.WALL_BG_COLOR})
    else if (t == "steel")
        block.attr({fill: bme.STEEL_BG_COLOR});
    else if (t == "player")
        block.attr({fill: bme.BOT_BG_COLOR});
    else
        block.attr({fill: bme.FREE_BG_COLOR});
};


/**
 * Clears canvas and resets internal variables.
 */
Bomber.MapEditor.clearMap = function() {
    var bme = Ext.ns("Bomber.MapEditor");
    if (bme.PAPER != null) {
        bme.PAPER.clear();
        var paper_el = bme.PAPER.canvas;
        paper_el.parentNode.removeChild(paper_el);
        bme.PAPER = null;
        bme.MAP = null;
    }
};


/**
 * Map drawing function.
 */
Bomber.MapEditor.drawMap = function() {
    var bme = Ext.ns("Bomber.MapEditor");
    bme.clearMap();
    // map dimensions in cells
    bme.MAP_HEIGHT = parseInt(Ext.get("height-fld").dom.value);
    if (bme.MAP_HEIGHT == undefined)
        bme.MAP_HEIGHT = bme.DEFAULT_HEIGHT;
    bme.MAP_WIDTH = parseInt(Ext.get("width-fld").dom.value);
    if (bme.MAP_WIDTH == undefined)
        bme.MAP_WIDTH = bme.DEFAULT_WIDTH;
    //
    bme.PAPER = Raphael("map-canvas",
                        bme.MAP_HEIGHT * bme.LENGTH + bme.MAP_HEIGHT * bme.SPACE + bme.SPACE,
                        bme.MAP_WIDTH * bme.LENGTH + bme.MAP_WIDTH * bme.SPACE + bme.SPACE);
    bme.MAP = bme.PAPER.set();
    var row = bme.PAPER.set();
    var cell = null;
    for (var h = 0; h < bme.MAP_HEIGHT; h++) {
        for (var w = 0; w < bme.MAP_WIDTH; w++) {
            cell = bme.PAPER.rect(w * bme.LENGTH + bme.SPACE * w,
                                  h * bme.LENGTH + bme.SPACE * h,
                                  bme.LENGTH, bme.LENGTH);
            row.push(cell);
        }
        bme.MAP.push(row);
        row = bme.PAPER.set();
    }
    bme.MAP.attr("fill", bme.FREE_BG_COLOR);
    bme.MAP.click(function(event) { bme.clickHandler(this, "click-type-sel", event) });
    bme.MAP.dblclick(function(event) { bme.clickHandler(this, "dclick-type-sel", event) });
};
