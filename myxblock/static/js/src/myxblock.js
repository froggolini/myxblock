/* Javascript for MyXBlock. */
function MyXBlock(runtime, element) {
    
    function updateLink(result) {
        $("#webAccess").show();
        $(".create-lab").attr("disabled", true);
        $('.iframe', element).attr('src', result.container);
        $("a").prop("href", result.web_url) 
    }

    function resetLink() {
        $('.iframe', element).attr('src', "about:blank");
        $("a").prop("href", "") 
        $("#myElem").show(1000);
        $(".create-lab").attr("disabled", false);
        $("#webAccess").hide(1000);
        $("#myElem").hide(5000);
     
    }

    var handlerStartUrl = runtime.handlerUrl(element, 'create_container');

    $('.create-lab', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerStartUrl,
            data: JSON.stringify({"hello": "world"}),
            success: updateLink
        });
    });

    var handlerStopUrl = runtime.handlerUrl(element, 'stop_container');

    $('.stop-lab', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerStopUrl,
            data: JSON.stringify({"hello": "world"}),
            success: resetLink
        });
    });


    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
