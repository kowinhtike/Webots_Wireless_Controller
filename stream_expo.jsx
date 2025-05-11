import { useEffect, useRef } from "react";
import { StyleSheet, View } from "react-native";
import { Button } from "react-native-paper";
import WebView from "react-native-webview";
import { io } from "socket.io-client";

export default function App() {
  const socketRef = useRef(null);

  useEffect(() => {
    // Replace with your local IP
    socketRef.current = io("http://192.168.1.6:3000");

    socketRef.current.on("connect", () => {
      console.log("Connected to WebSocket server");
    });

    socketRef.current.on("message", (msg) => {
      console.log("Received:", msg);
    });

    return () => {
      socketRef.current.disconnect();
    };
  }, []);

  const sendMessage = (cmd = "S") => {
    socketRef.current.emit("control", cmd);
  };

  return (
    <View style={styles.root}>
      <View style={{backgroundColor:"red",width:"100%",height:300}}>
         <WebView
        source={{ uri: 'http://192.168.1.6:3000/video_feed' }}  // <-- IP Change Here
        javaScriptEnabled={true}
        domStorageEnabled={true}
        allowsInlineMediaPlayback={true}
      />
      </View>
      <View style={styles.btnContainer}>
      <Button
      style={styles.btn}
        mode="contained"
        onPressIn={() => sendMessage("F")} onPressOut={()=> sendMessage()}
      >
        {"F"}
      </Button>
      <View style={styles.btnHorizontal}>
        <Button
      style={styles.btn}
        mode="contained"
        onPressIn={() => sendMessage("L")} onPressOut={()=> sendMessage()}
      >
        {"<"}
      </Button>
      <Button
      style={styles.btn}
        mode="contained"
        onPressIn={() => sendMessage("R")} onPressOut={()=> sendMessage()}
      >
        {">"}
      </Button>
      </View>
      <Button
      style={styles.btn}
        mode="contained"
        onPressIn={() => sendMessage("B")} onPressOut={()=> sendMessage()}
      >
        {"B"}
      </Button>
    </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root:{
    flex:1,
    alignItems:"center",
    justifyContent:"center"
  },
  btnContainer:{
    marginTop:50,
    alignItems:"center",
    justifyContent:"center"
  },
  btn:{
    width:80,
    padding:10
  },
  btnHorizontal:{
    flexDirection:"row",
    width:200,
    justifyContent:"space-between"
  }
})
