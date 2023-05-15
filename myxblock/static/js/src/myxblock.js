/* Javascript for MyXBlock. */
function MyXBlock(runtime, element, xblock_type) {
    var acc = document.getElementsByClassName("accordion");
    var i;

    for (i = 0; i < acc.length; i++) {
    acc[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var panel = this.nextElementSibling;
        if (panel.style.maxHeight) {
        panel.style.maxHeight = null;
        } else {
        panel.style.maxHeight = panel.scrollHeight + "px";
        }
    });
    }

    function updateLink(result) {
        $('.placeholderXss').toggle(xblock_type.type === 'xss');
        $('.placeholderSqli').toggle(xblock_type.type === 'sqli');
        $(".create-lab").attr("disabled", true);
        $('.iframe', element).attr('src', result.container);

        if (xblock_type.type === "sqli") {
            $("#webAccess a").prop("href", result.web_url) 
            $("#phpAccess a").prop("href", result.php_url) 
            $("#sshAccess a").text(result.ssh_ip)
            $("#dbAccess a").text(result.db_ip) 
        } else if (xblock_type.type === "xss") {
            $("#webAccess a").prop("href", result.web_url) 
        }
        
    }

    function resetLink() {
        $('.iframe', element).attr('src', "about:blank");
        $("#webAccess a").prop("href", "") 
        $("#phpAccess a").prop("href", "") 
        $("#dbAccess a").prop("href", "") 

        $("#myElem").show(1000);
        $(".create-lab").attr("disabled", false);
        $('.placeholderXss').hide(xblock_type.type === 'xss');
        $('.placeholderSqli').hide(xblock_type.type === 'sqli');
        $("#myElem").hide(5000);
        $('#time').toggle();
     
    }
    

    var handlerStartUrl = runtime.handlerUrl(element, 'create_container');
    
    $('.create-lab', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerStartUrl,
            data: JSON.stringify({"imageName": xblock_type.type}),
            success: updateLink
        });
        started = true
        setTimeout(function() {
            $.ajax({
              type: "POST",
              url: handlerStopUrl,
              data: JSON.stringify({"imageName": xblock_type.type}),
              success: resetLink
            });
          }, 300000);
    });

    var handlerStopUrl = runtime.handlerUrl(element, 'stop_container');

    $('.stop-lab', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: handlerStopUrl,
            data: JSON.stringify({"imageName": xblock_type.type}),
            success: resetLink
        });
    });


    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
