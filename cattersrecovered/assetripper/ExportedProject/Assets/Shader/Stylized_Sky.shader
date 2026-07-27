Shader "Stylized/Sky" {
	Properties {
		[Header(Sun Disc)] _SunDiscColor ("Color", Vector) = (1,1,1,1)
		_SunDiscMultiplier ("Multiplier", Float) = 25
		_SunDiscExponent ("Exponent", Float) = 125000
		[Header(Sun Halo)] _SunHaloColor ("Color", Vector) = (0.8970588,0.7760561,0.6661981,1)
		_SunHaloExponent ("Exponent", Float) = 125
		_SunHaloContribution ("Contribution", Range(0, 1)) = 0.75
		[Header(Horizon Line)] _HorizonLineColor ("Color", Vector) = (0.9044118,0.8872592,0.7913603,1)
		_HorizonLineExponent ("Exponent", Float) = 4
		_HorizonLineContribution ("Contribution", Range(0, 1)) = 0.25
		[Header(Sky Gradient)] _SkyGradientTop ("Top", Vector) = (0.172549,0.5686274,0.6941177,1)
		_SkyGradientBottom ("Bottom", Vector) = (0.764706,0.8156863,0.8509805,1)
		_SkyGradientExponent ("Exponent", Float) = 2.5
	}
	//DummyShaderTextExporter
	SubShader{
		Tags { "RenderType" = "Opaque" }
		LOD 200

		Pass
		{
			HLSLPROGRAM
			#pragma vertex vert
			#pragma fragment frag

			float4x4 unity_ObjectToWorld;
			float4x4 unity_MatrixVP;

			struct Vertex_Stage_Input
			{
				float4 pos : POSITION;
			};

			struct Vertex_Stage_Output
			{
				float4 pos : SV_POSITION;
			};

			Vertex_Stage_Output vert(Vertex_Stage_Input input)
			{
				Vertex_Stage_Output output;
				output.pos = mul(unity_MatrixVP, mul(unity_ObjectToWorld, input.pos));
				return output;
			}

			float4 frag(Vertex_Stage_Output input) : SV_TARGET
			{
				return float4(1.0, 1.0, 1.0, 1.0); // RGBA
			}

			ENDHLSL
		}
	}
}