/* Javascript for MyXBlock. */
function MyXBlock(runtime, element) {
    var imageName = ""

    function updateLink(result) {
        $(".placeholder").show();
        $(".create-lab").attr("disabled", true);
        $('.iframe', element).attr('src', result.container);
        $("#webAccess a").prop("href", result.web_url) 
        $("#phpAccess a").prop("href", result.php_url) 
        $("#sshAccess a").prop("href", result.ssh_ip) 
        $("#dbAccess a").prop("href", result.db_ip) 
    }

    function resetLink() {
        $('.iframe', element).attr('src', "about:blank");
        $("#webAccess a").prop("href", "") 
        $("#phpAccess a").prop("href", "") 
        $("#dbAccess a").prop("href", "") 
        $("#myElem").show(1000);
        $(".create-lab").attr("disabled", false);
        $(".placeholder").hide(1000);
        $("#myElem").hide(5000);
     
    }

    var handlerStartUrl = runtime.handlerUrl(element, 'create_container');
    
    $('.create-lab', element).click(function(eventObject) {
        var selectedOption = $('#selector').find(':selected')[0].value;
        if (selectedOption === "sqli") {
            imageName = "sqli";
        } else if (selectedOption === "xss") {
            imageName = "xss";
        }
        $.ajax({
            type: "POST",
            url: handlerStartUrl,
            data: JSON.stringify({"imageName": imageName}),
            success: updateLink
        });
    });

    var handlerStopUrl = runtime.handlerUrl(element, 'stop_container');

    $('.stop-lab', element).click(function(eventObject) {
        var selectedOption = $('#selector').find(':selected')[0].value;
        if (selectedOption === "sqli") {
            imageName = "sqli";
        } else if (selectedOption === "xss") {
            imageName = "xss";
        }
        $.ajax({
            type: "POST",
            url: handlerStopUrl,
            data: JSON.stringify({"imageName": imageName}),
            success: resetLink
        });
    });


    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
