 {% load static %}

<!-- favicon to avoid favicon error in browsers -->
<link rel="shortcut icon" href="{% static '/images/favicon.ico' %}" type="image/x-icon" />

	<div style="text-align:center;">
	<figure class="row" style="margin:5px;">
		<img src="{% static '/images/darwin_banner.jpg' %}" alt="darwin_banner" width="1290px" height="80px">
	</figure>
	<div class="row" style="margin:5px;">
		<div class="col-md-10" style="background-color:#777;margin:0px;padding:0px;color:white;text-align:center;font-weight:bold;text-decoration-color:white;font-size:20px;height:30px;">DATASET VIEW AND DEPURATION</div>
		<div id="proj_head" class="col-md-2" style="background-color:#EEE;margin:0px;padding:5px;text-align:center;font-weight:bold;font-size:12px;height:30px;border:solid 1px;"></div>
	</div>
</div>

<script type="text/javascript">$("#proj_head").text(sessionStorage.getItem("proj_name"));</script>

