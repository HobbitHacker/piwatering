/* 
 * Copyright Andy Styles, 2016. All Rights Reserved.
 */
$(function()
{
    function valveOn(valve) {
        jQuery.ajax({
            type    : "POST",
            url     : "/watering/von/" + valve,
            success : function(response) {
                $("#m" + valve).html(response);
                $("#mob-m" + valve).html(response);
                valveOnState(valve);
            },
            error: function (event, xhr, settings, thrownError) {
                $("#m" + valve).html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
                $("#mob-m" + valve).html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
            }
        });
    }
    
    
    function valveOff(valve) {
        jQuery.ajax({
            type    : "POST",
            url     : "/watering/voff/" + valve,
            success : function(response) {
                $("#m" + valve).html(response);
                $("#mob-m" + valve).html(response);
                valveOffState(valve);            },
            error: function (event, xhr, settings, thrownError) {
                $("#m" + valve).html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
                $("#mob-m" + valve).html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
                
            }
        });
    }
    
    
    function valveOnState(valve) {
        $("#r" + valve).addClass("success");
        $("#s" + valve).html("On");
        $("#act" + valve).html("Deactivate");
        $("#act" + valve).removeClass("btn-success").addClass("btn-danger");                
        $("#act" + valve).data("valve-state", "on");
        
        $("#mob-r" + valve).removeClass("bg-info bg-success").addClass("bg-success");
        $("#mob-s" + valve).html("On"); 
        $("#mob-act" + valve).removeClass("glyphicon-flash").addClass("glyphicon-ban-circle");
        $("#mob-act" + valve).removeClass("btn-success").addClass("btn-danger");                
        $("#mob-act" + valve).data("valve-state", "on");
    }
    
    
    function valveOffState(valve) {
        $("#r" + valve).removeClass("success");
        $("#s" + valve).html("Off");
        $("#act" + valve).html("Activate");
        $("#act" + valve).addClass("btn-success").removeClass("btn-danger");                
        $("#act" + valve).data("valve-state", "off");
        
        $("#mob-r" + valve).removeClass("bg-success").addClass($("mob-r" + valve).data("off-color"));
        $("#mob-s" + valve).html("Off");
        $("#mob-act" + valve).addClass("glyphicon-flash").removeClass("glyphicon-ban-circle");
        $("#mob-act" + valve).addClass("btn-success").removeClass("btn-danger");                
        $("#mob-act" + valve).data("valve-state", "off");
    }
    
    
    function valveState() {
        jQuery.ajax({
            type    : "GET",
            url     : "/watering/vstate",
            datatype: 'json',
            success: function(response) {
                for(v in response) {
                    vs = response[v];
                    if (vs.status == 'On') {
                        $("#m" + vs.valve).html(vs['left']);
                        $("#mob-m" + vs.valve).html(vs['left']);
                        valveOnState(vs.valve);
                    }
                    else {
                        $("#m" + vs.valve).html(" ");                       
                        $("#mob-m" + vs.valve).html(" ");                       
                        valveOffState(vs.valve);                            
                    }   
                }
            },
            error: function (event, xhr, settings, thrownError) {
                $("#m" + vs.valve).html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
            }
        });
    }
    
    function getHist()
    {

    	jQuery.ajax(
	{
		type: "GET",
		url: "/watering/gethistory",
                datatype: 'json',
		success: function(response)
		{
                    $("#history").html(response)
		},
            	error: function (event, xhr, settings, thrownError)
		{
	                $("#message").html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
		}
        });
    }


    
    $("body").on('click', ".valve-btn", function()
    {        
        var valveState = $(this).data("valve-state");
        valve = $(this).data("valve");	
        $(this).blur();
        
        if (valveState == "off") {
            valveOn(valve);
        }   
        else {
            valveOff(valve);
        }
    });
    
    $("body").on('click', ".edit-btn", function()
    {
        valve = $(this).data("valve");	
        $(this).blur();
        editName(valve);
    });
    
    // Status Panel - edit name button
    function editName(valve)
    {
        $("#oldName").text($("#name" + valve).text());
        $("#newName").val($("#name" + valve).text());
        $("#editName").data("valve", valve);
        $("#editName").modal("show");
    }
    
    $("#off").on('click', function()
    {
        $(this).blur();
    	jQuery.ajax(
	{
		type: "GET",
		url: "/watering/alloff",
		success: function(response)
		{
                    valveState();
                    $("#message").html(response);
                    $("#message").removeClass("hidden");

		},
            	error: function (event, xhr, settings, thrownError)
		{
                    $("#message").removeClass("hidden");
                    $("#message").html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
                }
        });
        
    });

    $("#schedule-table").on("click", ".btn", function() 
    {
        $(this).blur();
        p = $(this).parent().parent();
                window.location.assign("/watering/edit?day="+p.attr("day")+"&start="+p.attr("start")+"&valve="+p.attr("valve")+"&duration="+p.attr("duration")+"&dayn="+p.attr("dayn"));
    });	    
    
    // Edit Name Dialog - cancel button
    $("body").on('click', "#editCancel", function()
    {
            $("#editName").modal("hide");
    });

    // Edit Name Dialog - ok button
    $("body").on('click', "#editOK", function()
    {
        $(this).blur();
        jQuery.ajax(
        {
            type: "POST",
            url: "/watering/editname",
            contentType: 'application/json;charset=UTF-8',
            data:   JSON.stringify({
                        valve : $("#editName").data("valve"),
                        newName : $("#newName").val()}),
            dataType: 'text',
            success: function(response)
            {
                    $("#name" + $("#editName").data("valve")).text($("#newName").val())
                    $("#message").html("Valve name updated");
                    $("#message").removeClass("hidden");

            },
            error: function (event, xhr, settings, thrownError)
            {
                    $("#message").removeClass("hidden");
                    $("#message").html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
            }
        });
        $("#editName").modal("hide");
    });

    // Edit Schedule - Delete icon
    $("body").on("click", ".delete-icon", function() {
        $(this).blur();
        var thisRow = $(this).attr("id").substr(6);
        $("#deleteName").text($("#schedule" + thisRow).attr("name"));
        $("#deleteName").attr("valve",$("#schedule" + thisRow).attr("valve"));
        $("#deleteDay").text($("#schedule" + thisRow).attr("day"));
        $("#deleteDay").attr("dayNum",$("#schedule" + thisRow).attr("dayn"));
        $("#deleteStart").text($("#schedule" + thisRow).attr("start"));
        $("#deleteDuration").text($("#schedule" + thisRow).attr("duration"));
        $("#deleteSchedule").modal("show");
    });    
    
    // Delete Schedule - Cancel button
    $("body").on('click', "#deleteCancel", function()
    {
            $("#deleteSchedule").modal("hide");
    });    
    
    // Delete Schedule - Delete button
    $("body").on('click', "#deleteOK", function()
    {
        $(this).blur();
        jQuery.ajax(
        {
            type: "POST",
            url: "/watering/delsched",
            contentType: 'application/json;charset=UTF-8',
            data:   JSON.stringify({
                        valve : parseInt($("#deleteName").attr("valve")),
                        dayn  : parseInt($("#deleteDay").attr("dayNum")),
                        start : $("#deleteStart").text(),
                        duration: $("#deleteDuration").text(),
                        day : $("#deleteDay").text()
               }),
            dataType: 'text',
            success: function(response)
            {
//                    $(this).parent().parent().remove();
//                    $("#message").html("Schedule deleted.");
//                    $("#message").removeClass("hidden");
                    location.reload();

            },
            error: function (event, xhr, settings, thrownError)
            {
                    $("#message").removeClass("hidden");
                    $("#message").html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
            }
        });

    });    
    
    
    // Edit Schedule - Update button
    $("body").on('click', "#edit", function()
    {
        $(this).blur();
        
        jQuery.ajax(
            {
                type: "POST",
                url: "/watering/updsched",
                contentType: 'application/json;charset=UTF-8',
                data:   JSON.stringify({
                    valve : parseInt($("#valve option:selected").val()),
                    dayn  : parseInt($("#day option:selected").val()),
                    start : $("#starthour option:selected").val() + ":" + $("#startmin option:selected").val() + ":00",
                    duration: "00:" + $("#durmin option:selected").val() + ":" + $("#dursec option:selected").val(),
                    olddayn  : parseInt($("#day").attr("incoming")),
                    oldstart : $("#start").attr("incoming"),
                    oldduration: $("#duration").attr("incoming")                                    
                }),
                dataType: 'text',
                success: function(response)
                {
                    $(this).parent().parent().remove();
                    $("#message").html("Schedule updated.");
                    $("#message").removeClass("hidden");
                    
                },
                error: function (event, xhr, settings, thrownError)
                {
                    $("#message").removeClass("hidden");
                    $("#message").html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
                }
            });
    });    
    

    // Edit Schedule - Insert button
    $("body").on('click', "#insert", function()
    {
        $(this).blur();
        
        jQuery.ajax(
            {
                type: "POST",
                url: "/watering/inssched",
                contentType: 'application/json;charset=UTF-8',
                data:   JSON.stringify({
                    valve : parseInt($("#valve option:selected").val()),
                    dayn  : parseInt($("#day option:selected").val()),
                    start : $("#starthour option:selected").val() + ":" + $("#startmin option:selected").val() + ":00",
                    duration: "00:" + $("#durmin option:selected").val() + ":" + $("#dursec option:selected").val(),
                             
                }),
                dataType: 'text',
                success: function(response)
                {
                    $(this).parent().parent().remove();
                    $("#message").html("Schedule inserted.");
                    $("#message").removeClass("hidden");
                    
                },
                error: function (event, xhr, settings, thrownError)
                {
                    $("#message").removeClass("hidden");
                    $("#message").html(thrownError + "<br>" + xhr.status + " - " + xhr.responseText);
                }
            });
    }); 
    
    getHist();
    v = setInterval(valveState, 2000);
    h = setInterval(getHist, 2000);

});

